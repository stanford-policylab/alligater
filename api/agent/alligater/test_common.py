import unittest
from dataclasses import dataclass

from .common import simple_object


class TestCommon(unittest.TestCase):
    def test_simple_object(self):
        @dataclass
        class Foo:
            id: str
            bar: int

        assert simple_object(Foo(id="a", bar=1)) == {
            "id": "a",
            "bar": 1,
        }
        assert simple_object(Foo(id="a", bar=1), with_type=True) == {
            "type": "Foo",
            "value": {
                "id": "a",
                "bar": 1,
            },
        }

        @dataclass
        class Bar:
            foo: str
            zap: int

            @property
            def id(self):
                return f"{self.foo}-{self.zap}"

        assert simple_object(Bar(foo="a", zap=1)) == {
            "foo": "a",
            "zap": 1,
            "id": "a-1",
        }
        assert simple_object(Bar(foo="a", zap=1), with_type=True) == {
            "type": "Bar",
            "value": {
                "foo": "a",
                "zap": 1,
                "id": "a-1",
            },
        }
