import re
from collections.abc import Iterable, Sequence

from .common import hash_id, utcnow


class _MetaExpression(type):
    """Metaclass for all expressions."""

    def __getitem__(self, other):
        """Compose one function with another, in the form f(g(x)).

        This enables syntactic sugar, for example defining the "not equals"
        object as:
        Ne = Not[Eq]

        Args:
            other - function to compose

        Returns:
            Composed expression.
        """
        return _ComposedExpression(self, other)

    def __repr__(self) -> str:
        return self.__name__


class _Expression(metaclass=_MetaExpression):
    """Base class for an arbitrary expression.

    This implements boolean algebra on expressions; expression can be compared
    to each other with the standard equality or ordering operations.
    """

    def __eq__(self, other):
        return Eq(self, other)

    def __ne__(self, other):
        return Ne(self, other)

    def __lt__(self, other):
        return Lt(self, other)

    def __le__(self, other):
        return Le(self, other)

    def __gt__(self, other):
        return Gt(self, other)

    def __ge__(self, other):
        return Ge(self, other)

    def in_(self, other):
        return In(self, other)

    def or_(self, other):
        return Or(self, other)

    def and_(self, other):
        return And(self, other)

    def has(self, other):
        # Note __contains__ coerces to bool so we can't use it here.
        return Has(self, other)

    def matches(self, other):
        return Matches(self, other)

    def validate(self):
        """Validation for an expression can be implemented in a subclass."""
        pass

    def __call__(self, *args, log=None, context=None):
        """This is the actual behavior of the operator.

        This must be implemented in a subclass."""

        raise NotImplementedError()

    def equivalent(self, other):
        """Check whether two expressions are equivalent.

        Args:
            other - another _Expression

        Returns:
            True if expressions are the same.
        """
        if not isinstance(other, _Expression):
            return False

        return str(self) == str(other)

    def _trace(self, log, args, result):
        """Emit a EvalFunc trace event. If there is no logger passed, this is
        a no-op.

        Args:
            log - Log function (can be None)
            args - List of (evaluated) arguments used for evaluating this
            expression.
            result - Evaluation result
        """
        if not log:
            return
        name = self.__class__.__name__
        log(name, args, result)

    def to_json(self):
        return str(self)


class _ComposedExpression(_Expression):
    """Composition operator, as g(f(x))."""

    def __init__(self, g, f):
        self.outer = g
        if isinstance(f, Iterable):
            self.inners = f
        else:
            self.inners = (f,)

    def __call__(self, *args, **kwargs):
        # kwargs are contextual things like `log` that should be shared across
        # all invocations.
        inner_args = [f(*args, **kwargs) for f in self.inners]
        return self.outer(*inner_args, **kwargs)

    def __repr__(self):
        all_reps = [repr(inner) for inner in self.inners]
        if len(self.inners) == 1:
            inners = all_reps[0]
        else:
            inners = ", ".join(all_reps)
        return f"{repr(self.outer)}({inners})"


class _NullaryExpression(_Expression):
    """Expression of the form `operator()`."""

    def __init__(self):
        pass

    def evaluate(self, *args, log=None, context=None):
        pass


class _UnaryExpression(_Expression):
    """Expression of the form `operator(a)`."""

    def __init__(self, arg):
        self.arg = arg

    def evaluate(self, *args, log=None, context=None):
        arg = self.arg

        if callable(arg):
            arg = arg(*args, log=log, context=context)

        return arg

    def __repr__(self):
        op = repr(self.__class__)
        return f"{op}({repr(self.arg)})"


class _BinaryExpression(_Expression):
    """Expression of the form `operator(a, b)`."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, *args, log=None, context=None):
        left = self.left
        right = self.right

        if callable(left):
            left = left(*args, log=log, context=context)

        if callable(right):
            right = right(*args, log=log, context=context)

        return left, right

    def __repr__(self):
        op = repr(self.__class__)
        return f"{op}({repr(self.left)}, {repr(self.right)})"


class _InfixExpression(_BinaryExpression):
    """BinaryExpression with the representation `a <operator> b`."""

    def __repr__(self):
        op = repr(self.__class__)

        # Apply parentheses to sub-expressions if they are infix expressions.
        # Other notations are not ambiguous.
        if isinstance(self.left, _InfixExpression):
            left = f"({repr(self.left)})"
        else:
            left = repr(self.left)

        if isinstance(self.right, _InfixExpression):
            right = f"({repr(self.right)})"
        else:
            right = repr(self.right)

        return f"{left} {op} {right}"


class _NAryExpression(_Expression):
    def __init__(self, *args):
        self.args = args

    def evaluate(self, *fargs, log=None, context=None):
        return [
            a(*fargs, log=log, context=context) if callable(a) else a for a in self.args
        ]

    def __repr__(self):
        op = repr(self.__class__)
        args = [repr(a) for a in self.args]
        return f"{op}({', '.join(args)})"


# Operator definitions
#
# These are all the operators available to expressions.


class Literal(_UnaryExpression):
    """A literal value."""

    def __call__(self, *args, log=None, context=None):
        arg = self.evaluate(*args, log=log, context=context)

        self._trace(log, [arg], arg)

        return arg

    def __repr__(self):
        return repr(self.arg)


class Or(_InfixExpression):
    """Boolean 'or' operator."""

    def __call__(self, *args, log=None, context=None):
        left, right = self.evaluate(*args, log=log, context=context)
        result = left or right

        self._trace(log, [left, right], result)

        return result


class And(_InfixExpression):
    """Boolean 'and' operator."""

    def __call__(self, *args, log=None, context=None):
        left, right = self.evaluate(*args, log=log, context=context)
        result = left and right

        self._trace(log, [left, right], result)

        return result


class Not(_UnaryExpression):
    """Negate a value."""

    def __call__(self, *args, log=None, context=None):
        arg = self.evaluate(*args, log=log, context=context)
        result = not arg

        self._trace(log, [arg], result)

        return result


class Eq(_InfixExpression):
    """Equals operator."""

    def __call__(self, *args, log=None, context=None):
        left, right = self.evaluate(*args, log=log, context=context)
        result = left == right

        self._trace(log, [left, right], result)

        return result


Ne = Not[Eq]  # type: ignore
"""Not equals operator."""


class Lt(_InfixExpression):
    """Less than operator."""

    def __call__(self, *args, log=None, context=None):
        left, right = self.evaluate(*args, log=log, context=context)
        result = left < right

        self._trace(log, [left, right], result)

        return result


class Le(_InfixExpression):
    """Less than or equal to operator."""

    def __call__(self, *args, log=None, context=None):
        left, right = self.evaluate(*args, log=log, context=context)
        result = left <= right

        self._trace(log, [left, right], result)

        return result


Gt = Not[Le]  # type: ignore
"""Greater than operator."""


Ge = Not[Lt]  # type: ignore
"""Greater than or equal to operator."""


class In(_InfixExpression):
    """Containment operator

    If the left side is a collection, this returns True if *any* of the left
    side are in the right.
    """

    def __call__(self, *args, log=None, context=None):
        left, right = self.evaluate(*args, log=log, context=context)

        # Treat `None` as an empty list
        if right is None:
            right = []

        result = False
        if isinstance(left, Sequence) and not isinstance(left, str):
            result = any((x in right for x in left))
        else:
            result = left in right

        self._trace(log, [left, right], result)

        return result


def Has(left, right):
    """Reversed notation of `In`."""
    return In(right, left)


class Concat(_NAryExpression):
    """Concatenation operator."""

    def __call__(self, *args, log=None, context=None):
        args = self.evaluate(*args, log=log, context=context)
        val = "".join([str(a) for a in args])

        self._trace(log, args, val)

        return val


class Hash(_UnaryExpression):
    """Compute the assignment hash of a value."""

    def __call__(self, *args, log=None, context=None):
        arg = self.evaluate(*args, log=log, context=context)
        val = hash_id(str(arg))

        self._trace(log, [arg], val)

        return val


class Len(_UnaryExpression):
    """Get length of an iterable."""

    def __call__(self, *args, log=None, context=None):
        arg = self.evaluate(*args, log=log, context=context)
        val = len(arg)

        self._trace(log, [arg], val)

        return val


class Matches(_InfixExpression):
    """Perform a regular expression match.

    Example:
        $my_prop Matches '.*'
    """

    def __call__(self, *args, log=None, context=None):
        left, right = self.evaluate(*args, log=log, context=context)

        if left is None:
            left = ""
        if right is None:
            right = ""

        result = re.search(right, left) is not None

        self._trace(log, [left, right], result)

        return result


class Now(_NullaryExpression):
    """Get current time."""

    def __call__(self, *args, log=None, context=None):
        now_fn = utcnow

        if context and "now" in context:
            now_fn = context["now"]

        result = now_fn()

        self._trace(log, [], result)

        return result


class TimeSince(_BinaryExpression):
    """Get amount of time elapsed since a moment in the given unit.

    Example:
        TimeSince($my_prop, 'months')
    """

    _CONVERSIONS = {
        unit: conversion
        for units, conversion in [
            ({"s", "sec", "second", "seconds"}, 1.0),
            ({"m", "min", "minute", "minutes"}, 60.0),
            ({"h", "hr", "hour", "hours"}, 3_600.0),
            ({"d", "day", "days"}, 86_400.0),
            ({"w", "wk", "week", "weeks"}, 604_800.0),
            ({"mo", "mon", "month", "months"}, 2_628_288.0),
            ({"y", "yr", "year", "years"}, 31_536_000.0),
        ]
        for unit in units
    }

    def __call__(self, *args, log=None, context=None):
        now_ts = Now()(*args, log=log, context=context)
        moment, unit = self.evaluate(*args, log=log, context=context)

        delta = now_ts - moment
        seconds = delta.total_seconds()
        result = self._convert(seconds, unit)

        self._trace(log, [now_ts, moment, unit], result)
        return result

    def _convert(self, seconds, unit):
        unit = unit.lower()
        try:
            conversion = self._CONVERSIONS[unit.lower()]
            return seconds / conversion
        except KeyError:
            raise ValueError(f"Invalid unit '{unit}'")


class TrimPrefix(_BinaryExpression):
    """Remove a prefix from a string.

    Example:
        TrimPrefix($my_prop, 'prefix')
    """

    def __call__(self, *args, log=None, context=None):
        s, prefix = self.evaluate(*args, log=log, context=context)

        if not isinstance(s, str):
            raise TypeError(f"Expect {type(s)} to be str")

        result = s.removeprefix(prefix)

        self._trace(log, [s, prefix], result)

        return result


class TrimSuffix(_BinaryExpression):
    """Remove a suffix from a string.

    Example:
        TrimSuffix($my_prop, 'suffix')
    """

    def __call__(self, *args, log=None, context=None):
        s, suffix = self.evaluate(*args, log=log, context=context)

        if not isinstance(s, str):
            raise TypeError(f"Expect {type(s)} to be str")

        result = s.removesuffix(suffix)

        self._trace(log, [s, suffix], result)

        return result


# Global registry of all functions available to the DSL.
FUNCTION_REGISTRY = {}


def register_function(name: str, func: type[_Expression]):
    """Register a function in the global registry."""
    FUNCTION_REGISTRY[name] = func


# Pre-register public functions in this file
_init_globals = globals().copy()
for _name, _func in _init_globals.items():
    if (
        isinstance(_func, type)
        and issubclass(_func, _Expression)
        and not _name.startswith("_")
    ):
        register_function(_name, _func)
