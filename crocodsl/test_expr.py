import unittest
from datetime import datetime, UTC

from .expr import parse
from .field import _Field
from .func import Concat, Hash, In, Literal, Ge, Gt, Le, Lt, Eq, Not, Or, And, Ne


class TestExpr(unittest.TestCase):
    def test_parse_literal(self):
        """Test parsing into simple values."""
        assert parse("None")() is None
        assert parse("1")() == 1
        assert parse("1234")() == 1234
        assert parse("1.2")() == 1.2
        assert parse("True")() is True
        assert parse("False")() is False
        assert parse("0")() == 0
        assert parse("0.123")() == 0.123
        assert parse("-100")() == -100
        assert parse("-100.001")() == -100.001
        assert parse('"hello"')() == "hello"
        assert parse(r'"say \"hi\""')() == 'say "hi"'
        assert parse(r"'say \'hi\''")() == "say 'hi'"
        assert (
            parse(
                """
            "this 'should' work"
        """
            )()
            == "this 'should' work"
        )
        assert (
            parse(
                """
            'this "should" work'
        """
            )()
            == 'this "should" work'
        )
        assert parse("[1,2,3]")() == [1, 2, 3]
        assert parse("[True, 'hi', 1, 2.5, [1,2,3], None]")() == [
            True,
            "hi",
            1,
            2.5,
            [1, 2, 3],
            None,
        ]
        assert parse(r"'hi\nwith\tescapes'")() == "hi\nwith\tescapes"

    def test_parse_field(self):
        """Test parsing field attributes."""
        assert parse("$id")(None) is None
        assert parse("$id")({}) is None
        assert parse("$id")({"id": 123}) == 123
        assert parse("$id")({"foo": 123}) is None
        assert parse("[1, 2, $id]")({"id": 3}) == [1, 2, 3]

    def test_nested_field(self):
        """Test accessing nested fields."""
        d = {"a": {"b": "c"}}
        assert parse("$a.$b")(d) == "c"

        class A:
            def foo(self, *, value):
                return {"value": value}

        assert parse("$foo.$value")(A(), context={"value": "hi"}) == "hi"
        assert (
            parse("Concat($foo.$value, ', you') Eq 'hi, you'")(
                A(), context={"value": "hi"}
            )
            is True
        )

    def test_parse_compare(self):
        """Parse comparisons."""
        assert parse("1 Eq 1").equivalent(Eq(1, 1))
        assert parse("1 Ne 2").equivalent(Not(Eq(1, 2)))
        assert parse("1 Lt 2").equivalent(Lt(1, 2))
        assert parse("1 Le 2").equivalent(Le(1, 2))
        assert parse("2 Gt 1").equivalent(Gt(2, 1))
        assert parse("2 Ge 1").equivalent(Ge(2, 1))
        assert parse("1 In [1, 2, 3]").equivalent(In(1, [1, 2, 3]))

    def test_parse_logical(self):
        """Parse logical and/or."""
        assert parse("1 Eq 1 And 2 Ne 3").equivalent(And(Eq(1, 1), Ne(2, 3)))
        assert parse("1 Eq 1 Or 2 Ne 2").equivalent(Or(Eq(1, 1), Ne(2, 2)))
        assert parse("(1 Eq 1) Or (2 Ne 2)").equivalent(Or(Eq(1, 1), Ne(2, 2)))
        assert parse("Not(1 Eq 1 Or 2 Eq 2)").equivalent(Not(Or(Eq(1, 1), Eq(2, 2))))

    def test_function(self):
        """Test calling other functions."""
        assert parse("Hash('foo')").equivalent(Hash("foo"))
        assert parse("Hash('foo')")() == 0.8845447504445093
        assert parse("Hash(Concat($prefix, ':', $id))").equivalent(
            Hash(Concat(_Field("prefix"), ":", _Field("id")))
        )
        assert (
            parse("Hash(Concat($prefix, ':', $id))")({"prefix": "pfx", "id": "123"})
            == 0.07302924453117249
        )

        orig_ts = datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC)
        now_ts = datetime(2020, 1, 3, 3, 0, 0, tzinfo=UTC)
        assert parse("TimeSince($timestamp, 'd') Gt 2")(
            {"timestamp": orig_ts}, context={"now": lambda: now_ts}
        )
        assert parse("TimeSince($timestamp, 'd') Lt 3")(
            {"timestamp": orig_ts}, context={"now": lambda: now_ts}
        )

    def test_time_since_missing_value(self):
        """Test that calling TimeSince with a missing value raises a TypeError."""
        now_ts = datetime(2020, 1, 3, 3, 0, 0, tzinfo=UTC)

        with self.assertRaises(TypeError):
            parse("TimeSince($timestamp, 'd') Gt 2")(
                {}, context={"now": lambda: now_ts}
            )

    def test_compose(self):
        """More tests for composition of operators."""
        assert parse("Hash(Concat('test-', $id)) Lt 0.5").equivalent(
            Hash(Concat("test-", _Field("id"))) < 0.5
        )
        # "test-foo" hashes to: 0.6399548871841495
        assert parse("Hash(Concat('test-', $id)) Lt 0.5")({"id": "foo"}) is False

        assert parse("Hash($id) Lt 0.5 Or $id In ['a', 'b', 'c']").equivalent(
            Or(Hash(_Field("id")) < 0.5, _Field("id").in_(["a", "b", "c"]))
        )
        # "c" hashes to 0.5555553092364088, but is in the list
        assert parse("Hash($id) Lt 0.5 Or $id In ['a', 'b', 'c']")({"id": "c"}) is True

        assert parse(
            "(Concat($first_name, ' ', $last_name) Matches 'foo') Or ($outcomes Has 'xyz')"
        ).equivalent(
            Concat(_Field("first_name"), " ", _Field("last_name"))
            .matches("foo")
            .or_(_Field("outcomes").has("xyz"))
        )

    def test_inverse(self):
        """Test that str reps of parses are also parsable."""

        def t(exp, s):
            assert str(exp) == s
            assert exp.equivalent(parse(s))
            assert parse(s).equivalent(exp)

        t(Literal(1), "1")
        t(Literal("foo"), "'foo'")
        t(Literal("fo\no"), "'fo\\no'")
        t(Literal(r'"foo"'), """'"foo"'""")
        t(Literal(r'"fo\"o"'), r"""'"fo\\"o"'""")
        t(Literal(True), "True")
        t(Literal(False), "False")
        t(Literal([1, 2, 3]), "[1, 2, 3]")
        t(
            Literal([None, False, [1, 2, "foo", 55.123, -43.41]]),
            "[None, False, [1, 2, 'foo', 55.123, -43.41]]",
        )
        t(Ne("foo", "bar"), "Not('foo' Eq 'bar')")
        t(Gt(10, 9), "Not(10 Le 9)")
        t(Ge(10, 9), "Not(10 Lt 9)")
        t(Hash("foo"), "Hash('foo')")
        t(Hash(_Field("foo")), "Hash($foo)")
        t(
            Hash(Concat("prefix", ":", _Field("foo"))),
            "Hash(Concat('prefix', ':', $foo))",
        )
        t(Eq(_Field("id"), "foo"), "$id Eq 'foo'")
        t(
            And(_Field("id") == "foo", Hash(_Field("id")) < 0.5),
            "($id Eq 'foo') And (Hash($id) Lt 0.5)",
        )
        t(
            Concat(_Field("first_name"), " ", _Field("last_name"))
            .matches("foo")
            .or_(_Field("outcomes").has("xyz")),
            "(Concat($first_name, ' ', $last_name) Matches 'foo') Or ('xyz' In $outcomes)",
        )

    def test_syntax_error_trailing(self):
        """Test calling an undefined function."""
        with self.assertRaises(SyntaxError):
            # Gte should be Ge
            parse("TimeSince($assigned, 'mo') Gte 6")
