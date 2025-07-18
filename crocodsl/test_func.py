import unittest
from datetime import UTC, datetime

import crocodsl.func as func


class TestFunc(unittest.TestCase):
    def test_op_repr(self):
        """Test the representations of the operators."""
        assert repr(func.Eq) == "Eq"
        assert repr(func.Ne) == "Not(Eq)"
        assert repr(func.And) == "And"
        assert repr(func.Or) == "Or"
        assert repr(func.Not) == "Not"
        assert repr(func.Lt) == "Lt"
        assert repr(func.Le) == "Le"
        assert repr(func.Gt) == "Not(Le)"
        assert repr(func.Ge) == "Not(Lt)"
        assert repr(func.In) == "In"
        assert repr(func.Concat) == "Concat"
        assert repr(func.Hash) == "Hash"
        assert repr(func.Len) == "Len"
        assert repr(func.Matches) == "Matches"
        assert repr(func.Now) == "Now"
        assert repr(func.TimeSince) == "TimeSince"

    def test_expr_repr(self):
        """Test the representations of expressions."""
        assert repr(func.Eq("a", "b")) == "'a' Eq 'b'"
        assert repr(func.Ne("a", "b")) == "Not('a' Eq 'b')"
        assert (
            repr(
                func.And(
                    func.Eq("a", "a"),
                    func.Lt(10, 11),
                )
            )
            == "('a' Eq 'a') And (10 Lt 11)"
        )
        assert (
            repr(
                func.Or(
                    func.Eq("a", "b"),
                    func.Lt(10, 11),
                )
            )
            == "('a' Eq 'b') Or (10 Lt 11)"
        )
        assert repr(func.Not(True)) == "Not(True)"
        assert repr(func.Le(10, 10)) == "10 Le 10"
        assert repr(func.Gt(11, 10)) == "Not(11 Le 10)"
        assert repr(func.Ge(11, 10)) == "Not(11 Lt 10)"
        assert repr(func.In("a", ["a", "b", "c"])) == "'a' In ['a', 'b', 'c']"
        assert repr(func.Concat("a", "b", "c")) == "Concat('a', 'b', 'c')"
        assert repr(func.Hash("foo")) == "Hash('foo')"
        assert repr(func.Has([1, 2, 3], 1) == "1 In [1, 2, 3]")
        assert repr(func.Matches("Foo", r".*") == "'Foo' Matches '.*'")

    def test_eq(self):
        """Test equality."""
        assert func.Eq("a", "a")() is True
        assert func.Eq("a", "b")() is False
        assert func.Eq(1, 1)() is True
        assert func.Eq(1, 0)() is False

    def test_ne(self):
        """Test inequality."""
        assert func.Ne("a", "a")() is False
        assert func.Ne("a", "b")() is True
        assert func.Ne(1, 1)() is False
        assert func.Ne(1, 0)() is True

    def test_and(self):
        """Test and."""
        assert (
            func.And(
                func.Eq("a", "a"),
                func.Eq(1, 1),
            )()
            is True
        )
        assert (
            func.And(
                func.Eq("a", "a"),
                func.Eq(1, 0),
            )()
            is False
        )
        assert (
            func.And(
                func.Eq("a", "b"),
                func.Eq(1, 0),
            )()
            is False
        )
        assert (
            func.And(
                func.Eq("a", "b"),
                func.Eq(1, 1),
            )()
            is False
        )

    def test_or(self):
        """Test or."""
        assert (
            func.Or(
                func.Eq("a", "a"),
                func.Eq(1, 1),
            )()
            is True
        )
        assert (
            func.Or(
                func.Eq("a", "a"),
                func.Eq(1, 0),
            )()
            is True
        )
        assert (
            func.Or(
                func.Eq("a", "b"),
                func.Eq(1, 0),
            )()
            is False
        )
        assert (
            func.Or(
                func.Eq("a", "b"),
                func.Eq(1, 1),
            )()
            is True
        )

    def test_not(self):
        """Test negation."""
        assert func.Not(True)() is False
        assert func.Not(False)() is True

    def test_lt(self):
        """Test < equality."""
        assert func.Lt(10, 11)() is True
        assert func.Lt(11, 11)() is False
        assert func.Lt(12, 11)() is False

    def test_le(self):
        """Test <= equality."""
        assert func.Le(10, 11)() is True
        assert func.Le(11, 11)() is True
        assert func.Le(12, 11)() is False

    def test_gt(self):
        """Test > equality."""
        assert func.Gt(10, 11)() is False
        assert func.Gt(11, 11)() is False
        assert func.Gt(12, 11)() is True

    def test_ge(self):
        """Test > equality."""
        assert func.Ge(10, 11)() is False
        assert func.Ge(11, 11)() is True
        assert func.Ge(12, 11)() is True

    def test_in(self):
        """Test containment."""
        assert func.In("a", ["a", "b", "c"])() is True
        assert func.In("b", ["a", "b", "c"])() is True
        assert func.In("c", ["a", "b", "c"])() is True
        assert func.In("x", ["a", "b", "c"])() is False
        assert func.In("x", None)() is False

    def test_has(self):
        """Test reverse containment."""
        assert func.Has(["a", "b", "c"], "a")() is True
        assert func.Has(["a", "b", "c"], "b")() is True
        assert func.Has(["a", "b", "c"], "c")() is True
        assert func.Has(["a", "b", "c"], "x")() is False
        assert func.Has(None, "x")() is False

    def test_concat(self):
        """Test concatenation."""
        assert func.Concat("a", "b", "c")() == "abc"

    def test_hash(self):
        """Test hashing."""
        assert func.Hash("abc")() == 0.7054175881782409

    def test_len(self):
        """Test length."""
        assert func.Len([1, 2, 3]) == 3
        assert func.Len("abc") == 3
        assert (
            func.Len(
                (
                    "a",
                    "b",
                )
            )
            == 2
        )
        assert func.Len({"a": 1, "b": 2, "c": 3}) == 3

    def test_matches(self):
        """Test regex matching."""
        assert func.Matches("foo", r".*")() is True
        assert func.Matches("foo", r"^f")() is True
        assert func.Matches("bar", r"^f")() is False
        assert func.Matches("a.b.c", r"\.b\.")() is True

    def test_now(self):
        """Test now function."""
        ts = datetime(2024, 1, 2, 3, 4, 5, tzinfo=UTC)
        assert func.Now()(context={"now": lambda: ts}) == ts

    def test_time_since(self):
        """Test time delta computation."""
        orig_ts = datetime(2024, 1, 1, 3, 4, 5, tzinfo=UTC)
        ts = datetime(2024, 1, 2, 3, 4, 5, tzinfo=UTC)
        assert func.TimeSince(orig_ts, "seconds")(context={"now": lambda: ts}) == 86_400
        assert func.TimeSince(orig_ts, "minutes")(context={"now": lambda: ts}) == 1_440
        assert func.TimeSince(orig_ts, "hours")(context={"now": lambda: ts}) == 24
        assert func.TimeSince(orig_ts, "d")(context={"now": lambda: ts}) == 1
        assert func.TimeSince(orig_ts, "w")(context={"now": lambda: ts}) == 1 / 7
        assert (
            func.TimeSince(orig_ts, "mo")(context={"now": lambda: ts})
            == 86_400 / 2_628_288
        )
        assert func.TimeSince(orig_ts, "y")(context={"now": lambda: ts}) == 1 / 365

    def test_trim_prefix(self):
        """Test removal of characters from a string."""
        assert repr(func.TrimPrefix("abc", "b")) == "TrimPrefix('abc', 'b')"
        assert func.TrimPrefix("abc", "ab")() == "c"
        assert func.TrimPrefix("abc", "a")() == "bc"
        assert func.TrimPrefix("abc", "c")() == "abc"
        assert func.TrimPrefix("prefixabc", "pref")() == "ixabc"
        with self.assertRaises(TypeError):
            func.TrimPrefix(None, "a")()
        with self.assertRaises(TypeError):
            func.TrimPrefix("abc", None)()

    def test_trim_suffix(self):
        """Test removal of characters from a string."""
        assert repr(func.TrimSuffix("abc", "b")) == "TrimSuffix('abc', 'b')"
        assert func.TrimSuffix("abc", "bc")() == "a"
        assert func.TrimSuffix("abc", "c")() == "ab"
        assert func.TrimSuffix("abc", "a")() == "abc"
        assert func.TrimSuffix("abcsuffix", "suffix")() == "abc"
        with self.assertRaises(TypeError):
            func.TrimSuffix(None, "a")()
        with self.assertRaises(TypeError):
            func.TrimSuffix("abc", None)()

    def test_composition(self):
        """Make sure functions can be composed."""
        assert func.Hash(func.Concat("a", "b", "c"))() == 0.7054175881782409

    def test_dunders(self):
        """Test that expressions can be combined algebraically."""
        assert repr(func.Hash("abc") < 0.75) == "Hash('abc') Lt 0.75"
        assert (func.Hash("abc") < 0.75)() is True

        assert repr(func.Hash("abc") <= 0.75) == "Hash('abc') Le 0.75"
        assert (func.Hash("abc") <= 0.75)() is True

        assert repr(func.Hash("abc") > 0.7) == "Not(Hash('abc') Le 0.7)"
        assert (func.Hash("abc") > 0.7)() is True

        assert repr(func.Hash("abc") >= 0.7) == "Not(Hash('abc') Lt 0.7)"
        assert (func.Hash("abc") >= 0.7)() is True

        assert (
            repr(func.Hash("abc") == 0.7054175881782409)
            == "Hash('abc') Eq 0.7054175881782409"
        )
        assert (func.Hash("abc") == 0.7054175881782409)() is True

        assert repr(func.Hash("abc") != 0.7) == "Not(Hash('abc') Eq 0.7)"
        assert (func.Hash("abc") != 0.7)() is True

        assert repr(func.Lt(10, 11).and_(func.Lt(1, 2))) == "(10 Lt 11) And (1 Lt 2)"
        assert func.Lt(10, 11).and_(func.Lt(1, 2))() is True

        assert repr(func.Lt(10, 11).or_(func.Lt(2, 1))) == "(10 Lt 11) Or (2 Lt 1)"
        assert func.Lt(10, 11).or_(func.Lt(2, 1))() is True

        assert repr(func.Literal([1, 2, 3]).has(1)) == "1 In [1, 2, 3]"
        assert func.Literal([1, 2, 3]).has(1)() is True

    def test_register_function(self):
        """Test that functions can be registered."""

        class CustomFunc(func._UnaryExpression):
            """Compute the assignment hash of a value."""

            def __call__(self, *args, log=None, context=None):
                arg = self.evaluate(*args, log=log, context=context)
                val = str(arg) + "!!!"

                self._trace(log, [arg], val)

                return val

        func.register_function("AddExcitement", CustomFunc)

        import crocodsl.expr

        expr = crocodsl.expr.parse("AddExcitement('foo')")
        assert expr() == "foo!!!"
