from collections.abc import Iterable, Sequence

from .common import hash_id
import alligater.events as events



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

    def __repr__(self):
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
        return In(other, self)

    def validate(self):
        """Validation for an expression can be implemented in a subclass."""
        pass

    def __call__(self, *args, log=None):
        """This is the actual behavior of the operator.

        This must be implemented in a subclass."""

        raise NotImplemented()

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


class _ComposedExpression(_Expression):
    """Composition operator, as g(f(x))."""

    def __init__(self, g, f):
        self.outer = g
        if isinstance(f, Iterable):
            self.inners = f
        else:
            self.inners = (f,)

    def __call__(self, *args):
        inner_args = [f(*args) for f in self.inners]
        return self.outer(*inner_args)

    def __repr__(self):
        all_reps = [repr(inner) for inner in self.inners]
        if len(self.inners) == 1:
            inners = all_reps[0]
        else:
            inners = ", ".join(all_reps)
        return f"{repr(self.outer)}({inners})"


class _UnaryExpression(_Expression):
    """Expression of the form `operator(a)`."""

    def __init__(self, arg):
        self.arg = arg

    def evaluate(self, *args, log=None):
        arg = self.arg

        if callable(arg):
            arg = arg(*args, log=log)

        return arg

    def __repr__(self):
        op = repr(self.__class__)
        return f"{op}({repr(self.arg)})"


class _BinaryExpression(_Expression):
    """Expression of the form `operator(a, b)`."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def evaluate(self, *args, log=None):
        left = self.left
        right = self.right

        if callable(left):
            left = left(*args, log=log)

        if callable(right):
            right = right(*args, log=log)

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

    def evaluate(self, *fargs, log=None):
        return [a(*fargs, log=log) if callable(a) else a for a in self.args]

    def __repr__(self):
        op = repr(self.__class__)
        args = [repr(a) for a in self.args]
        return f"{op}({', '.join(args)})"



## Operator definitions
#
# These are all the operators available to expressions.


class Literal(_UnaryExpression):
    """A literal value."""

    def __call__(self, *args, log=None):
        arg = self.evaluate(*args, log=log)
        return arg

    def __repr__(self):
        return repr(self.arg)


class Or(_InfixExpression):
    """Boolean 'or' operator."""

    def __call__(self, *args, log=None):
        left, right = self.evaluate(*args, log=log)
        return left or right


class And(_InfixExpression):
    """Boolean 'and' operator."""

    def __call__(self, *args, log=None):
        left, right = self.evaluate(*args, log=log)
        return left and right


class Not(_UnaryExpression):
    """Negate a value."""

    def __call__(self, *args, log=None):
        arg = self.evaluate(*args, log=log)
        return not arg


class Eq(_InfixExpression):
    """Equals operator."""

    def __call__(self, *args, log=None):
        left, right = self.evaluate(*args, log=log)
        return left == right


Ne = Not[Eq]
"""Not equals operator."""


class Lt(_InfixExpression):
    """Less than operator."""

    def __call__(self, *args, log=None):
        left, right = self.evaluate(*args, log=log)
        return left < right


class Le(_InfixExpression):
    """Less than or equal to operator."""

    def __call__(self, *args, log=None):
        left, right = self.evaluate(*args, log=log)
        return left <= right


Gt = Not[Le]
"""Greater than operator."""


Ge = Not[Lt]
"""Greater than or equal to operator."""


class In(_InfixExpression):
    """Containment operator

    If the left side is a collection, this returns True if *any* of the left
    side are in the right.
    """

    def __call__(self, *args, log=None):
        left, right = self.evaluate(*args, log=log)

        result = False
        if isinstance(left, Sequence) and not isinstance(left, str):
            result = any((x in right for x in left))
        else:
            result = left in right

        events.EvalFunc(log, f=self.__class__.__name__, args=[left, right], result=result)

        return result


class Concat(_NAryExpression):
    """Concatenation operator."""

    def __call__(self, *args, log=None):
        args = self.evaluate(*args, log=log)
        return "".join([str(a) for a in args])


class Hash(_UnaryExpression):
    """Compute the assignment hash of a value."""

    def __call__(self, *args, log=None):
        arg = self.evaluate(*args, log=log)
        val = hash_id(str(arg))

        events.EvalFunc(log, f=self.__class__.__name__, args=[arg], result=val)

        return val
