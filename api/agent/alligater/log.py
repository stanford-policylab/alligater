import atexit
import signal
import threading
import sys
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime, timezone

import alligater.events as events
from .common import simple_object, encode_json



default_now = lambda: datetime.now(timezone.utc)
"""Default `now` implementation."""



class ObjectLogger:
    """Logger that aggregates event data as an object."""

    def __init__(self, write, trace=False, now=default_now, workers=1):
        """Create a new ObjectLogger with the given `write` callback.

        Args:
            write - Callback when event data is ready.
            trace - Whether to enable trace logging
            now - Function to get current datetime
            workers - Number of background workers to handle IO
        """
        self._now = now
        self._cv = threading.Condition()
        self._write = write
        self._cache = {}
        self._finished = []
        self._trace = trace
        self._stopped = False
        self._workers = [threading.Thread(
            name=f'ObjectLogger-io-{w}',
            target=self._write_results,
            daemon=True) for w in range(workers)]
        [w.start() for w in self._workers]

        # Cleanup threads and try to drain the queue if possible when exiting.
        atexit.register(self._drain)
        sigs = [signal.SIGINT, signal.SIGTERM]
        for sig in sigs:
            signal.signal(sig, self._drain)

    def __call__(self, event):
        """Log a single event."""
        # Every event tracks an ID that is unique to the invocation.
        call_id = event.call_id

        with self._cv:
            if event == events.EnterGate:
                self._cache[call_id] = {
                        'ts': self._now(),
                        'call_id': call_id,
                        'entity': simple_object(event.entity, with_type=True),
                        'feature': event.feature.to_dict(),
                        'assignment': None,
                        'variant': '',
                        'trace': None if not self._trace else [],
                        }

            if self._trace:
                cur = self._cache[call_id]
                d = event.asdict(exclude={
                    'call_id': cur['call_id'],
                    'entity': cur['entity']['value'],
                    'feature': cur['feature'],
                    }, compress=True)
                self._cache[call_id]['trace'].append(d)

            if event == events.ChoseVariant:
                # There might be nested variants that get chosen if the feature
                # is defined as a tree. In that case this will be called
                # multiple times, but only the last (leaf) variant will stick.
                self._cache[call_id]['variant'] = simple_object(event.variant)

            if event == events.LeaveGate:
                self._cache[call_id]['assignment'] = event.value
                self._finished.append(call_id)
                self._cv.notify()

    def _drain(self, *args):
        """Stop worker threads and drain the queue."""
        with self._cv:
            self._stopped = True
            self._cv.notify_all()

        [w.join() for w in self._workers]

        with self._cv:
            while len(self._finished) > 0:
                try:
                    self._write_unsafe()
                except (Exception, SystemExit):
                    continue

    def _write_results(self):
        """[THREAD] Loop over queue and write events as they are found."""
        with self._cv:
            while True:
                if self._stopped:
                    return

                if not self._finished:
                    self._cv.wait()
                    continue

                self._write_unsafe()

    def _write_unsafe(self):
        """Write the head of the queue if possible with no thread safety."""
        try:
            id_ = self._finished.pop(0)
            event = self._cache.pop(id_)
            self._write(event)
        except KeyError as e:
            print("Synchronization error writing event:", e)
        except IndexError:
            pass
        except Exception as e:
            print("Failed to write event:", e)


class NetworkLogger(ObjectLogger):
    """Logger that writes results over the network with retries."""

    def __init__(self,
            url,
            headers=None,
            auth=None,
            body=None,
            timeout=10.0,
            max_retries=3,
            backoff_factor=1.0,
            debug=False,
            **kwargs):
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
        adapter = HTTPAdapter(max_retries=Retry(
            total=max_retries,
            status_forcelist=[413, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "OPTIONS", "POST", "GET", "PUT", "TRACE", "DELETE"],
            backoff_factor=backoff_factor,
            ))
        http.mount("http://", adapter)
        http.mount("https://", adapter)
        http.auth = auth
        http.headers.update({
            'Content-Type': 'application/json; charset=utf-8',
            })
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
        self._debugw("Writing log", data)

        try:
            r = self._http.post(self._url,
                    timeout=self._timeout,
                    data=self._serialize(data))
        
            r.raise_for_status()
            self._debugw("Log written")
        except HTTPError as e:
            self._debugw("Failed to write log:", e)
        except Exception as e:
            self._debugw("Something unexpected happened:", e)

    def _debugw(self, *args):
        """Write a debug line.

        This is a no-op if debug mode is not enabled.

        Args:
            *args - anything
        """
        if not self._debug:
            return

        print("[NetworkLogger]", *args, file=sys.stderr)


class PrintLogger:
    """Logger that dumps events and features from feature evaluation."""

    def __init__(self, trace=False):
        """Create a new print logger.

        Args:
            trace - Whether to dump full trace of events in decision.
        """
        self._trace = trace

    def __call__(self, event):
        trace = self._trace

        if event == events.EnterGate:
            print("=== MAKING ASSIGNMENT ===")
            print("CallId:", event.call_id)
            print("Entity:", event.entity)
            print("Feature:", event.feature.to_dict())
            if trace:
                print("Trace:")

        if trace:
            print(str(event))

        if event == events.LeaveGate:
            print("Assignment:", event.value)
            print("=== END ASSIGNMENT ===")


default_logger = PrintLogger(trace=True)
"""Default Alligater logging function."""
