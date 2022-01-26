from functools import partial
import threading
import hashlib
import time

from .feature import Feature
from .variant import Variant
from .arm import Arm
from .rollout import Rollout
from .population import Population
from .common import ValidationError, MissingFeatureError
from .parse import parse_yaml, load_config
from .log import default_logger, ObjectLogger, PrintLogger
import alligater.func as func
import alligater.field as field



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

    def __init__(self,
            features=None,
            yaml=None,
            logger=default_logger,
            reload_interval=0,
            loader_kwargs=None,
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
            loader_kwargs - Arguments to pass to the config loader. See the
            method in `parse.py` for details.
        """

        if type(features) is list:
            features = {f.name: f for f in features}

        # Trace/event logging function
        self._logger = logger
        # Mutex for shared access to features dict from reloader thread.
        self._mtx = threading.Lock()
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

        # Start reloading. This will load one initial time on the main thread,
        # then (if `reload_interval` and `yaml` options are passed) will reload
        # at interval forever in a background thread.
        self._reload()

        if not self._features:
            print("[Warning] Alligater was instantiated without any features! Was this intentional?")

    def __getattr__(self, feature_name):
        """Get a function that will evaluate the given feature.

        Args:
            feature_name - Name of feature to evaluate

        Returns:
            Function that can be called with an `entity` to evaluate.
        """
        try:
            with self._mtx:
                ft = self._features[feature_name]
            return partial(self, ft)
        except KeyError:
            raise MissingFeatureError(feature_name)

    def __call__(self, feature, entity):
        """Evaluate an entity against the given feature.

        Args:
            feature - Feature to evaluate
            entity - Arbitrary entity to evaluate
        
        Returns:
            Value of the variant to return.
        """
        return feature(entity, log=self._logger)

    def _reload(self):
        """Start a background process to reload YAML at an interval."""
        # Force a synchronous run of the loader on the main thread
        self._run_reload(once=True)

        # Start a background loader to reload at interval.
        thread = threading.Thread(target=self._run_reload, args=())
        thread.daemon = True
        thread.start()

    def _run_reload(self, once=False):
        """Background worker to reload features from YAML.

        Args:
            once - Whether to force the loader to run only once, immediately.
        """
        while True:
            # Don't sleep if this is a one-time run.
            if not once:
                if not self._reload_interval:
                    print("[Warning] No reload interval passed; (re)loader is exiting.")
                    return
                time.sleep(self._reload_interval)

            if not self._yaml:
                print("[Warning] No YAML path is specified; (re)loader is exiting.")
                return

            try:
                yaml_str = load_config(self._yaml, **self._loader_kwargs)
                new_sum = self._checksum(yaml_str)
                if new_sum != self._old_sum:
                    with self._mtx:
                        # NOTE: When features are reloaded, they are **not**
                        # merged with the _current_ list of features, they are
                        # always merged with the original hardcoded list. This
                        # results in more predictable behavior -- if we always
                        # merged with the current list, transient mistakes in
                        # a config could propagate forever.
                        self._features = parse_yaml(yaml_str,
                                default_features=self._original_features)
                        self._old_sum = new_sum
            except Exception as e:
                print("[Warning] Alligater loader encountered an error:", e)

            # Exit if this is a one-time deal.
            if once:
                return

    def _checksum(self, s):
        """Compute checksum of a string.

        Args:
            s - String to hash

        Returns:
            Unique hash of the input
        """
        return hashlib.sha256(s.encode('utf-8')).hexdigest()



__all__ = [
        'Alligater',
        'Feature',
        'Variant',
        'Arm',
        'Rollout',
        'Population',
        'ValidationError',
        'func',
        'field',
        'events',
        ]
