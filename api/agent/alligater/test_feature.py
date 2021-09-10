import unittest

from .feature import Feature
from .rollout import Rollout
from .variant import Variant
from .population import Population
from .arm import Arm
from .field import _Field



class User:

    def __init__(self, id_):
        self.id = id_


class TestFeature(unittest.TestCase):

    def test_simplest(self):
        """Test the simplest configuration."""
        f = Feature(
                'test_feature',
                variants=[Variant('foo', 'Foo')],
                default_arm='foo',
                )

        # Everyone's a member, everyone gets the same ariant.
        assert f(User("one")) == "Foo"
        assert f(User("two")) == "Foo"
        assert f(User("three")) == "Foo"
        assert f(User("four")) == "Foo"

    def test_ab(self):
        """Simple A/B gate"""
        f = Feature(
                'ab_feature',
                variants=[
                    Variant('a', 'A'),
                    Variant('b', 'B'),
                    ],
                rollouts=[
                    Rollout(
                        Rollout.DEFAULT,
                        population=Population.DEFAULT,
                        arms=[
                            Arm('a', 0.5),
                            Arm('b', 0.5),
                            ],
                        ),
                    ],
                )

        # A/B are weighted 50/50. It's a coincidence that it works out
        # perfectly split here.
        # ID hashes to: 0.2812531000305875
        assert f(User("1")) == 'A'
        # ID hashes to: 0.010947509244765752
        assert f(User("2")) == 'A'
        # ID hashes to: 0.8328318262036765
        assert f(User("3")) == 'B'
        # ID hashes to: 0.937214106622131
        assert f(User("4")) == 'B'

    def test_complex(self):
        """More complicated gate."""
        f = Feature(
            name="multi_rollout_feature_full",
            variants=[
                Variant("a", "A"),
                Variant("b", "B"),
                Variant("off", None),
                ],
            default_arm=Arm("off"),
            rollouts=[
                Rollout(
                    name="test_segment_1",
                    population=Population.Percent(0.2, "my_seed"),
                    arms=[
                        Arm("a", weight=0.5),
                        Arm("b", weight=0.5),
                        ],
                    ),
                Rollout(
                    name="test_segment_2",
                    population=Population.Explicit(["id_1", "id_2", "id_26"]),
                    arms=[Arm("a", weight=1.0)],
                    ),
                ],
            )

        # The my_seed Population hashes to: 0.9791994382873984
        # So it gets the default variant.
        assert f(User("1")) is None

        # my_seed Population hashes to: 0.11176176296782649
        # test_segment_1 hashes to: 0.19817491497580958
        # So this gets variant `a`
        assert f(User("MemberID")) == 'A'

        # my_seed hashes to: 0.19481342807941482
        # test_segment_1 hashes to: 0.7498685567763539
        # So the user gets `b`, and *not* A as stated in the Explicit Rollout.
        assert f(User("id_26")) == 'B'

        # my_seed hashes to: 0.8810651836208253
        # So user falls through and gets `a` from the Explicit variant.
        assert f(User("id_2")) == 'A'

    def test_custom_field(self):
        """Explicit population based on custom entity field."""
        f = Feature(
            name="custom_field",
            variants=[
                Variant("a", "A"),
                Variant("off", None),
                ],
            default_arm=Arm("off"),
            rollouts=[
                Rollout(
                    name="test_segment_1",
                    population=Population.Explicit(
                        ["id_1", "id_2"],
                        id_field=_Field("custom")
                        ),
                    arms=[Arm("a", weight=1.0)],
                    ),
                ],
            )

        assert f({"id": "id_2"}) is None
        assert f({"custom": "id_2"}) == 'A'
        assert f({"custom": "other"}) is None
        # When the attribute returns a list, the `in` test uses ANY semantics.
        assert f({"custom": ["other", "id_2"]}) == 'A'
