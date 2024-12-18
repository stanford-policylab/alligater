import atexit
import hashlib
import threading
from functools import partial
from typing import Optional, Callable, Any, Tuple

from .arm import Arm
from .cache import AssignmentCache
from .common import (
    LoadError,
    MissingFeatureError,
    NoAssignment,
    NoConfig,
    NoReload,
    SkipLog,
    ValidationError,
    encode_json,
    simple_object,
    default_now,
    NowFn,
)
from .feature import Feature
from .events import EventLogger
from .log import (
    DeferrableLogger,
    NetworkLogger,
    ObjectLogger,
    PrintLogger,
    default_logger,
    log,
)
from .parse import load_config, parse_yaml, ConfigSource
from .population import Population
from .rand import seed
from .rollout import Rollout
from .value import CallType, Value
from .variant import Variant


StickyFn = Callable[[Feature, Any], Tuple[str, Any, int]]


class Alligater:
    """The Alligater object represents the universe of available features.

    The Alligater instance evaluates features to return an assignment. For
    example:

    ```
    gater = Alligater(yaml='path/to/my/features.yaml')

    # Assuming a feature with name "my_feature" was defined in the YAML:
    treatment = gater.my_feature(some_user)
    ```

    The Alligater instance can be configured with different modes of logging
    in order to preserve and/or debug the assignment decisions it makes.
    """

    def __init__(
        self,
        features: list[Feature] | dict[str, Feature] | None = None,
        yaml: ConfigSource | None = None,
        logger: EventLogger = default_logger,
        reload_interval: float = 0,
        sticky: StickyFn | None = None,
        loader_kwargs: dict | None = None,
        now: NowFn = default_now,
    ):
        """Create a new feature gater.

        Features can either come from a hardcoded predefined list or YAML.
        If YAML is specified, it will override the hardcoded list.

        Args:
            features - List or dictionary of features.
            yaml - Path to features specified in YAML.
            logger - Function to call to log decisions. See `events` for more
            information about how to interpret gating decisions.
            reload_interval - Number of seconds between checking for YAML changes
            sticky - Optional function to lookup previous assignments for the
            input entity. This will skip full evaluation.
            loader_kwargs - Arguments to pass to the config loader. See the
            method in `parse.py` for details.
            now - Function to call to get the current time.
        """
        log.info("🐊 Loading alligater ...")

        if isinstance(features, list):
            features = {f.name: f for f in features}

        # Current time
        self._now = now
        # Trace/event logging function
        self._logger = logger
        # Mutex for shared access to features dict from reloader thread.
        self._cv = threading.Condition()
        # Path to YAML config (either local or remote path)
        self._yaml = yaml
        # Current list of features
        self._features = features.copy() if features else {}
        # Original hard-coded list of features
        self._original_features = features.copy() if features else {}
        # Checksum of the currently loaded YAML config
        self._old_sum = ""
        # Number of seconds to wait between reloads
        self._reload_interval = reload_interval
        # Arguments for `load_config` (See `parse#load_config`.)
        self._loader_kwargs = loader_kwargs if loader_kwargs else {}
        # Sticky assignment fetcher
        self._sticky = sticky
        # Whether loader thread is stopped
        self._stopped = True
        # Background thread
        self._thread = None
        self._local_assignments = AssignmentCache()

        # Start reloading. This will load one initial time on the main thread,
        # then (if `reload_interval` and `yaml` options are passed) will reload
        # at interval forever in a background thread.
        try:
            self._reload()
        except NoConfig:
            log.warning("😭 No feature path specified for Alligater.")
        except NoReload:
            log.warning("😤 No reload interval specified for Alligater.")

        if not self._features:
            log.warning(
                "🤬 Alligater was instantiated without any features! Was this intentional?"
            )

    def __getattr__(self, feature_name):
        """Get a function that will evaluate the given feature.

        Args:
            feature_name - Name of feature to evaluate

        Returns:
            Function that can be called with an `entity` to evaluate.
        """
        try:
            with self._cv:
                ft = self._features[feature_name]
            return partial(self, ft)
        except KeyError as e:
            raise MissingFeatureError(feature_name) from e

    async def __call__(
        self, feature, entity, silent=False, deferred=None, now: Optional[NowFn] = None
    ):
        """Evaluate an entity against the given feature.

        Args:
            feature - Feature to evaluate
            entity - Arbitrary entity to evaluate
            silent - Whether to suppress logging for this invocation
            deferred - Whether exposure logging should be deferred. Note that
            assignment logging can never be deferred.
            now - Optional function to call to get the current time. (Overrides default.)

        Returns:
            Wrapped value of the variant to return.
        """
        logger = self._logger if not silent else None
        now_func = now if now else self._now
        value = await feature(
            entity,
            log=logger,
            sticky=self._sticky,
            assignment_cache=self._local_assignments,
            gater=self,
            now=now_func,
        )
        # Note that Logger implementations that aren't DeferrableLoggers
        # log immediately and calling `log` is just a no-op.
        if value.call_type == CallType.ASSIGNMENT:
            value.log()

        # Log an exposure immediately unless it's deferred.
        if not deferred:
            value.log()

        return value

    def stop(self):
        """Stop the background reloader."""
        # Make sure that the logger stops if it can.
        if self._logger and hasattr(self._logger, "stop"):
            self._logger.stop()

        # Stop internal loader thread if necessary.
        if self._stopped or not self._thread:
            return

        with self._cv:
            self._stopped = True
            self._cv.notify_all()
        self._thread.join()
        self._thread = None

    def _reload(self):
        """Start a background process to reload YAML at an interval."""
        if not self._stopped or self._thread:
            log.warning("👀 Called _reload when Alligater was already reloading")
            return

        # Force a synchronous run of the loader on the main thread
        # If this fails, it'll throw an error on the main thread.
        self._run_reload(once=True)

        # Start a background loader to reload at interval.
        if not self._reload_interval:
            raise NoReload("No reload interval passed; reloader will not run")
        thread = threading.Thread(target=self._run_reload, args=())
        self._stopped = False
        self._thread = thread
        thread.start()
        atexit.register(self.stop)

    def _run_reload(self, once=False):
        """Background worker to reload features from YAML.

        Args:
            once - Whether to force the loader to run only once, immediately.
        """
        while True:
            with self._cv:
                # Don't sleep if this is a one-time run.
                if not once:
                    self._cv.wait(timeout=self._reload_interval)
                    if self._stopped:
                        return

                if not self._yaml:
                    raise NoConfig("No YAML path is specified; (re)loader is exiting.")

                try:
                    log.debug("🕵️‍♀️  Checking for new features ...")
                    yaml_str = load_config(self._yaml, **self._loader_kwargs)
                    new_sum = self._checksum(yaml_str)
                    if new_sum != self._old_sum:
                        log.debug("🎉 New features found!")
                        # NOTE: When features are reloaded, they are **not**
                        # merged with the _current_ list of features, they are
                        # always merged with the original hardcoded list. This
                        # results in more predictable behavior -- if we always
                        # merged with the current list, transient mistakes in
                        # a config could propagate forever.
                        self._features = parse_yaml(
                            yaml_str,
                            default_features=self._original_features,
                            raise_exceptions=once,
                        )
                        self._old_sum = new_sum
                        log.debug("☺️  Updated to {}!".format(new_sum))
                        if once:
                            return
                    else:
                        log.debug("😔 No new features found")
                except Exception as e:
                    if once:
                        raise LoadError("Failed to load feature spec") from e
                    else:
                        log.error(
                            "😫 Alligater loader encountered an error: {}".format(e)
                        )

    def _checksum(self, s):
        """Compute checksum of a string.

        Args:
            s - String to hash

        Returns:
            Unique hash of the input
        """
        return hashlib.sha256(s.encode("utf-8")).hexdigest()


__all__ = [
    "Alligater",
    "Feature",
    "Variant",
    "Arm",
    "Rollout",
    "Population",
    "ValidationError",
    "events",
    "seed",
    "log",
    "encode_json",
    "simple_object",
    "DeferrableLogger",
    "NetworkLogger",
    "ObjectLogger",
    "PrintLogger",
    "NoAssignment",
    "SkipLog",
    "CallType",
    "Value",
]
