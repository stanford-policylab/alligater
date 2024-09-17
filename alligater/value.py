import math
from enum import Enum
from typing import Generic, Optional, TypeVar
from datetime import datetime

from .events import EventLogger
from .log import DeferrableLogger
from .common import NowFn, default_now


class CallType(Enum):
    ASSIGNMENT = "assignment"
    EXPOSURE = "exposure"


T = TypeVar("T")


class Value(Generic[T]):
    """Wrapper for a value returned by a feature gate.

    The value is stored in the `value` property. It is immutable. The wrapper
    class serves as a proxy, so you can interact with the value without ever
    unwrapping it in almost all cases.

    The wrapper contains the log function. If logging was deferred from the
    gate, you can call `.log()` on the wrapper to send the log to the server.
    Logs are always idempotent; it's impossible to write logs multiple times.

    If a log is deferred and never sent, it will be garbage collected.
    """

    def __init__(
        self,
        value: T,
        variant: str,
        call_id: Optional[str] = None,
        call_type: CallType = CallType.ASSIGNMENT,
        log: Optional[EventLogger] = None,
        now: NowFn = default_now,
    ):
        self._value = value
        self._variant = variant
        self._ts = now()
        self._call_id = call_id
        self._call_type = call_type
        self._log = log

    def __del__(self):
        """Clean up unsent logs when garbage collecting."""
        if isinstance(self._log, DeferrableLogger):
            self._log.drop_log(self._call_id)

    @property
    def value(self) -> T:
        """Unwrap the internal value."""
        return self._value

    @property
    def variant(self) -> str:
        """Get the variant name."""
        return self._variant

    @property
    def ts(self) -> datetime:
        """Get the timestamp the value was created."""
        return self._ts

    @property
    def call_type(self) -> CallType:
        """Check the type of call (assignment vs exposure)."""
        return self._call_type

    def log(self, extra: Optional[dict] = None):
        """Write a log to the server.

        Only needs to be called if the log is deferred.

        Args:
            extra - Optional additional data to log.
        """
        if isinstance(self._log, DeferrableLogger) and self._call_id:
            # Note that we *don't* override the timestamp here, even though we could.
            # There is some value in keeping the original value of the timestamp, since
            # it represents when a decision was made. There will be other timestamps when
            # the log gets ingested that will better represent when the exposure happened.
            self._log.write_log(self._call_id, extra=extra)
            # If the call type wasn't already an exposure, it should be now!
            self._call_type = CallType.EXPOSURE

    # == PROXY ALL THE DUNDER METHODS TO THE INTERNAL VALUE ==

    def __eq__(self, other):
        return self._value == other

    def __gt__(self, other):
        return self._value > other

    def __lt__(self, other):
        return self._value < other

    def __ge__(self, other):
        return self._value >= other

    def __le__(self, other):
        return self._value <= other

    def __ne__(self, other):
        return self._value != other

    def __hash__(self):
        return hash(self._value)

    def __format__(self, spec):
        return self._value.format(spec)

    def __bytes__(self):
        return bytes(self._value)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return repr(self._value)

    def __bool__(self):
        return bool(self._value)

    def __len__(self):
        return len(self._value)

    def __contains__(self, x):
        return x in self._value

    def __iter__(self):
        return iter(self._value)

    def __reversed__(self):
        return reversed(self._value)

    def __getitem__(self, k):
        return self._value[k]

    def __getattr__(self, name):
        return getattr(self._value, name)

    def __and__(self, other):
        return self._value & other

    def __xor__(self, other):
        return self._value ^ other

    def __or__(self, other):
        return self._value | other

    def __add__(self, other):
        return self._value + other

    def __mul__(self, other):
        return self._value * other

    def __sub__(self, other):
        return self._value - other

    def __truediv__(self, other):
        return self._value / other

    def __floordiv__(self, other):
        return self._value // other

    def __matmul__(self, other):
        return self._value @ other

    def __mod__(self, other):
        return self._value % other

    def __divmod__(self, other):
        return divmod(self._value, other)

    def __pow__(self, other, mod=None):
        return pow(self._value, other, mod=mod)

    def __lshift__(self, other):
        return self._value << other

    def __rshift__(self, other):
        return self._value >> other

    def __radd__(self, other):
        return other + self._value

    def __rsub__(self, other):
        return other - self._value

    def __rmul__(self, other):
        return other * self._value

    def __rmatmul__(self, other):
        return other @ self._value

    def __rtruediv__(self, other):
        return other / self._value

    def __rfloordiv__(self, other):
        return other // self._value

    def __rmod__(self, other):
        return other % self._value

    def __rdivmod__(self, other):
        return divmod(other, self._value)

    def __rpow__(self, other, mod=None):
        return pow(other, self._value, mod=mod)

    def __rlshift__(self, other):
        return other << self._value

    def __rrshift__(self, other):
        return other >> self._value

    def __rand__(self, other):
        return other & self._value

    def __ror__(self, other):
        return other | self._value

    def __rxor__(self, other):
        return other ^ self._value

    def __neg__(self):
        return -self._value

    def __pos__(self):
        return +self._value

    def __abs__(self):
        return abs(self._value)

    def __invert__(self):
        return ~self._value

    def __complex__(self):
        return complex(self._value)

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __round__(self, ndigits=None):
        return round(self._value, ndigits=ndigits)

    def __trunc__(self):
        return math.trunc(self._value)

    def __floor__(self):
        return math.floor(self._value)

    def __ceil__(self):
        return math.ceil(self._value)
