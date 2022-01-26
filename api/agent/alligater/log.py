import atexit
import signal
import threading
import sys
from datetime import datetime

import alligater.events as events
from .common import simple_object




class ObjectLogger:
    """Logger that aggregates event data as an object."""

    def __init__(self, write, trace=False, now=datetime.now, workers=1):
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
                        'entity': simple_object(event.entity),
                        'feature': event.feature.to_dict(),
                        'assignment': None,
                        'trace': None if not self._trace else [],
                        }

            if self._trace:
                cur = self._cache[call_id]
                d = event.asdict(exclude={
                    'call_id': cur['call_id'],
                    'entity': cur['entity'],
                    'feature': cur['feature'],
                    }, compress=True)
                self._cache[call_id]['trace'].append(d)

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
