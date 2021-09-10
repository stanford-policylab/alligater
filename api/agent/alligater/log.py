import alligater.events as events



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
