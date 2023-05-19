import unittest
from dataclasses import dataclass

import crocodsl.field as field
import crocodsl.func as func


@dataclass
class User:
    id: str


class TestField(unittest.TestCase):
    def test_entity_id(self):
        """Test getting the entity ID."""
        assert field.ID(User("abc")) == "abc"
        assert field.ID(User(123)) == 123

    def test_repr(self):
        """Test the representation of fields."""
        expr = func.Hash(field.ID) < 0.75
        assert repr(expr) == "Hash($id) Lt 0.75"

    def test_func(self):
        """Test fields can be used in expressions."""
        expr = field.ID == "abc"
        assert expr(User("abc")) is True
        assert expr(User(123)) is False

        expr2 = func.Hash(field.ID) < 0.75
        # Hash value is 0.7054175881782409
        assert expr2(User("abc")) is True

        expr3 = func.Hash(func.Concat("a", "b", field.ID)) > 0.75
        assert expr3(User("c")) is False

        expr4 = func.Hash(func.Concat("a", "b", field.ID)) == 0.7054175881782409
        assert expr4(User("c")) is True
        assert expr4(User("d")) is False

        expr5 = field.ID.in_(["a", "b", "c"])
        assert expr5(User("a")) is True
        assert expr5(User("b")) is True
        assert expr5(User("c")) is True
        assert expr5(User("d")) is False
