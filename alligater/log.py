import abc
import atexit
import copy
import logging
import signal
import threading
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from urllib3.util import Retry

import alligater.events as events

from .common import SkipLog, encode_json, seq_id, simple_object, default_now, NowFn

# Sys log (different than feature trace log)
log = logging.getLogger("alligater")


class DeferrableLogger(events.EventLogger):
    """Traits for a logger that can be deferred."""

    @abc.abstractmethod
    def write_log(self, call_id: str, extra: Optional[dict] = None):
        """Write the log with the given ID.

        Args:
            call_id - The UUID of the log to write
            extra - Extra data to send with this log
        """
        ...

    @abc.abstractmethod
    def drop_log(self, call_id: str):
        """Clear the log with the given ID without writing.

        This must be called to avoid memory leaks for dropped logs.
        """
        ...


class ObjectLogger(DeferrableLogger):
    """Logger that aggregates event data as an object."""

    def __init__(
        self,
        write,
        trace: bool = False,
        workers: int = 1,
        install_signals: bool = True,
    ):
        """Create a new ObjectLogger with the given `write` callback.

        Args:
            write - Callback when event data is ready.
            trace - Whether to enable trace logging
            workers - Number of background workers to handle IO
            install_signals - Whether to install signal handlers for cleanup.
                If you are running in an environment like uvicorn, there may be
                conflicts with signal handlers.
        """
        self._cv = threading.Condition()
        self._write = write
        self._cache = dict[str, dict]()
        self._finished = list[dict]()
        self._deferred = set[str]()
        self._trace = trace
        self._stopped = False
        self._workers = [
            threading.Thread(
                name=f"ObjectLogger-io-{w}", target=self._write_results, daemon=True
            )
            for w in range(workers)
        ]
        for w in self._workers:
            w.start()

        # Cleanup threads and try to drain the queue if possible when exiting.
        atexit.register(self._drain)
        if install_signals:
            sigs = [signal.SIGINT, signal.SIGTERM]
            for sig in sigs:
                signal.signal(sig, self._drain)

    def stop(self):
        """Shut off the logger and send any pending messages."""
        self._drain()

    def __call__(self, event, now: NowFn = default_now):
        """Log a single event."""
        # Every event tracks an ID that is unique to the invocation.
        call_id = event.call_id

        with self._cv:
            if event == events.EnterGate:
                self._cache[call_id] = {
                    "ts": now(),
                    "call_id": call_id,
                    "entity": simple_object(event.entity, with_type=True),
                    "feature": event.feature.to_dict(),
                    "assignment": None,
                    "variant": "",
                    "trace": None if not self._trace else [],
                    "repeat": False,
                    "sticky": False,
                }

            if self._trace:
                cur = self._cache[call_id]
                d = event.asdict(
                    exclude={
                        "call_id": cur["call_id"],
                        "entity": cur["entity"]["value"],
                        "feature": cur["feature"],
                    },
                    compress=True,
                )
                self._cache[call_id]["trace"].append(d)

            if event == events.ChoseVariant:
                # There might be nested variants that get chosen if the feature
                # is defined as a tree. In that case this will be called
                # multiple times, but only the last (leaf) variant will stick.
                self._cache[call_id]["variant"] = simple_object(event.variant)
                self._cache[call_id]["sticky"] = event.sticky

            # Get assigned variant from the sticky assignment if it exists.
            if event == events.StickyAssignment and event.assigned:
                self._cache[call_id].update(
                    {
                        "variant": {
                            "name": event.variant,
                        },
                        "repeat": True,
                        "sticky": True,
                    }
                )

            if event == events.LeaveGate:
                self._cache[call_id]["assignment"] = event.value
                # Note that log is not written immediately. Call `write_log` to
                # put it in the queue.
                self._deferred.add(call_id)

    def write_log(self, call_id, extra=None):
        """Write a deferred log by its ID."""
        with self._cv:
            if call_id not in self._deferred:
                return

            # Make a copy of the event data to write. This freezes the data at
            # this moment in time.
            data = copy.deepcopy(self._cache[call_id])
            # If this event has been sent before, generate a new ID for it.
            if data["repeat"]:
                data["call_id"] = seq_id(data["call_id"])

            # Add extra data if it's given during this call.
            if extra:
                data["extra"] = extra

            # Add to queue to publish.
            self._finished.append(data)
            # Mark the cached object as a repeat if it's logged again.
            self._cache[call_id]["repeat"] = True
            # Wake a sender thread to broadcast the log.
            self._cv.notify()

    def drop_log(self, call_id):
        """Drop a deferred log by its ID."""
        with self._cv:
            self._deferred.remove(call_id)
            try:
                del self._cache[call_id]
            except KeyError:
                pass

    def _drain(self, *args):
        """Stop worker threads and drain the queue."""
        if not self._stopped:
            log.debug("🙉 Stopping log write workers ...")
            with self._cv:
                self._stopped = True
                self._cv.notify_all()
            [w.join() for w in self._workers]
            self._workers = []

        with self._cv:
            if not self._finished:
                return

            log.debug("🪵 Draining pending logs ...")
            while len(self._finished) > 0:
                event = self._finished.pop(0)
                try:
                    self._write_handled(event)
                except SystemExit:
                    continue

    def _write_results(self):
        """[THREAD] Loop over queue and write events as they are found."""
        while not self._stopped:
            with self._cv:
                if not self._finished:
                    self._cv.wait()

                if self._stopped:
                    return

                event = self._finished.pop(0)
            # Release the lock to write event, so that other workers can write.
            self._write_handled(event)

    def _write_handled(self, event):
        """Write an event with error handling."""
        try:
            self._write(event)
        except Exception as e:
            log.error("😓 Failed to write event: {}".format(e))


class NetworkLogger(ObjectLogger):
    """Logger that writes results over the network with retries."""

    def __init__(
        self,
        url,
        headers=None,
        auth=None,
        body=None,
        timeout=10.0,
        max_retries=5,
        backoff_factor=1.0,
        debug=False,
        **kwargs,
    ):
        """Create a logger that sends data to a remote endpoint.

        Args:
            url - Endpoint to log to
            headers - Key/value hash of headers to include in every request.
            This may include `Authorization` and `Content-Type` headers. The
            default content type is `application/json; charset=utf-8`.
            auth - Optional basic auth tuple
            body - Function to serialize the input log object to a string. By
            default this just does a standard JSON serialization.
            timeout - Time to wait for server response before giving up. The
            default is 10s.
            max_retries - Number of times to reattempt requests, default is 3.
            backoff_factor - Exponential backoff factor; see requests docs.
            debug - Whether to print log lines to stderr in addition to sending
            them over the network.
            **kwargs - See ObjectLogger.__init__
        """
        self._url = url
        self._debug = debug
        self._body = body
        self._timeout = timeout

        # Configure http adapter
        http = requests.Session()
        adapter = HTTPAdapter(
            max_retries=Retry(
                total=max_retries,
                status_forcelist=[413, 429, 500, 502, 503, 504],
                allowed_methods=[
                    "HEAD",
                    "OPTIONS",
                    "POST",
                    "GET",
                    "PUT",
                    "TRACE",
                    "DELETE",
                ],
                backoff_factor=backoff_factor,
            )
        )
        http.mount("http://", adapter)
        http.mount("https://", adapter)
        http.auth = auth
        http.headers.update(
            {
                "Content-Type": "application/json; charset=utf-8",
            }
        )
        if headers:
            http.headers.update(headers)
        self._http = http

        # Configure the base ObjectLogger.
        super().__init__(self._post, **kwargs)

    def _serialize(self, data):
        """Convert data to string.

        If the `body` function passed on init does not convert the data to a
        string itself, the default JSON encoder will stringify the output of
        the body function.

        Args:
            data - Event data

        Returns:
            Serialized string of data to send over network.
        """
        if self._body:
            data = self._body(data)

        if not isinstance(data, str):
            data = encode_json(data)

        return data

    def _post(self, data):
        """Write data over the network.

        Args:
            data - Log to write
        """
        self._debugw("Writing log: {}", data)

        try:
            s = self._serialize(data)
            r = self._http.post(self._url, timeout=self._timeout, data=s)

            r.raise_for_status()
            self._debugw("Log written")
        except HTTPError as e:
            self._debugw("Failed to write log: {}", e)
        except SkipLog:
            self._debugw("Skipping writing log (intentionally)")
        except Exception as e:
            self._debugw("Something unexpected happened: {}", e)

    def _debugw(self, *args):
        """Write a debug line.

        This is a no-op if debug mode is not enabled.

        Args:
            *args - anything
        """
        if not self._debug:
            return

        log.debug("🪵  " + args[0].format(*args[1:]))


class PrintLogger(events.EventLogger):
    """Logger that dumps events and features from feature evaluation."""

    def __init__(self, trace: bool = False):
        """Create a new print logger.

        Args:
            trace - Whether to dump full trace of events in decision.
        """
        self._trace = trace

    def __call__(self, event, now: NowFn = default_now):
        trace = self._trace

        if event == events.EnterGate:
            print("=== MAKING ASSIGNMENT ===")
            print("CallId:", event.call_id)
            print("Entity:", event.entity)
            print("Feature:", event.feature.to_dict())
            print("Current time:", now())
            if trace:
                print("Trace:")

        if trace:
            print(str(event))

        if event == events.ChoseVariant:
            print("Variant:", event.variant)
            print("Sticky:", event.sticky)

        if event == events.LeaveGate:
            print("Assignment:", event.value)
            print("=== END ASSIGNMENT ===")


default_logger = PrintLogger(trace=True)
"""Default Alligater logging function."""
