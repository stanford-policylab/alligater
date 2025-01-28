import unittest
import tempfile
import pytest

import responses
from responses import matchers
import alligater.parse as parse
from crocodsl.field import _Field
from crocodsl.func import Hash, TrimPrefix

from .arm import Arm
from .feature import Feature
from .population import Population
from .rollout import Rollout
from .variant import Variant

FIXTURES = {
    # The simplest possible gate specification.
    "simple": {
        "feature": Feature(
            "simplest_feature",
            variants=[Variant("foo", "This is the only value")],
            default_arm=Arm("foo"),
        ),
        "yaml": """
        feature:
          name: simplest_feature
          variants:
            foo: This is the only value
          # Automatically roll out `foo` to everyone.
          default_arm: foo
        """,
    },
    # Simple A/B gate
    "simple_ab": {
        "feature": Feature(
            "ab_feature",
            variants=[
                Variant("a", "This is the value for 'a'"),
                Variant("b", "This is the value for 'b'"),
            ],
            rollouts=[
                Rollout(arms=[Arm("a"), Arm("b")]),
            ],
        ),
        "yaml": """
        feature:
          name: ab_feature
          variants:
            a: This is the value for 'a'
            b: This is the value for 'b'
          rollouts:
            # Automatically rollout to everyone with a 50/50 split.
            - arms:
              - a
              - b
        """,
    },
    # Fully specified A/B gate with unequal weights.
    "full_ab": {
        "feature": Feature(
            "ab_feature_full",
            variants=[
                Variant("a", "This is the value for 'a'"),
                Variant("b", "This is the value for 'b'"),
            ],
            rollouts=[
                Rollout(
                    name="default",
                    population=Population.DEFAULT,
                    arms=[
                        Arm("a", 0.25),
                        Arm("b", 0.75),
                    ],
                ),
            ],
        ),
        "yaml": """
        feature:
          name: ab_feature_full
          variants:
            a: This is the value for 'a'
            b: This is the value for 'b'
          rollouts:
            - name: default
              population: default
              arms:
                - variant: a
                  weight: 0.25
                - variant: b
                  weight: 0.75
        """,
    },
    # A/B with custom rollout randomizer
    "full_ab_custom": {
        "feature": Feature(
            "ab_feature_custom_randomizer",
            variants=[
                Variant("a", "This is the value for 'a'"),
                Variant("b", "This is the value for 'b'"),
            ],
            rollouts=[
                Rollout(
                    name="default",
                    population=Population.DEFAULT,
                    arms=[
                        Arm("a", 0.25),
                        Arm("b", 0.75),
                    ],
                    randomizer=Hash(_Field("custom")),
                ),
            ],
        ),
        "yaml": """
        feature:
          name: ab_feature_custom_randomizer
          variants:
            a: This is the value for 'a'
            b: This is the value for 'b'
          rollouts:
            - name: default
              population: default
              arms:
                - variant: a
                  weight: 0.25
                - variant: b
                  weight: 0.75
              randomizer: Hash($custom)
        """,
    },
    # Gate with multiple rollouts and populations. The second rollout is implied
    # from the `default_arm` setting.
    "multi_rollout": {
        "feature": Feature(
            "multi_rollout_feature",
            variants=[
                Variant("on", True),
                Variant("off", False),
            ],
            default_arm="off",
            rollouts=[
                Rollout(
                    name="test_segment",
                    population=Population.Percent(0.2, "some_seed"),
                    arms=["on"],
                ),
            ],
        ),
        "yaml": """
        feature:
          name: multi_rollout_feature
          variants:
            "on": true
            "off": false
          default_arm: "off"
          rollouts:
            - name: test_segment
              population:
                type: percent
                value: 0.2
                seed: some_seed
              arms:
                - "on"
        """,
    },
    # Fully-specified gate with multiple populations.
    "full_rollout": {
        "feature": Feature(
            name="multi_rollout_feature_full",
            variants=[
                Variant("a", "A"),
                Variant("b", "B"),
                Variant("off", None),
            ],
            default_arm=Arm("off"),
            rollouts=[
                Rollout(
                    name="temp_assignment_segment",
                    population=Population.Explicit(["id_temp"]),
                    arms=[Arm("off", weight=1.0)],
                    sticky=False,
                ),
                Rollout(
                    name="test_segment_1",
                    population=Population.Percent(0.2, "some_seed"),
                    arms=[
                        Arm("a", weight=0.5),
                        Arm("b", weight=0.5),
                    ],
                ),
                Rollout(
                    name="test_segment_2",
                    population=Population.Explicit(["id_1", "id_2", "id_3", "id_4"]),
                    arms=[Arm("a", weight=1.0)],
                ),
                Rollout(
                    name="test_segment_3",
                    population=Population.Percent(
                        0.5, "third_seed", id_field=_Field("non_standard_id")
                    ),
                    arms=["b", "off"],
                ),
            ],
        ),
        "yaml": """
        feature:
          name: multi_rollout_feature_full
          variants:
            a: 'A'
            b: 'B'
            "off": null
          default_arm: "off"
          rollouts:
            - name: temp_assignment_segment
              sticky: false
              population:
                type: explicit
                value: [id_temp]
              arms:
                - variant: "off"
                  weight: 1.0
            - name: test_segment_1
              population:
                type: percent
                value: 0.2
                seed: some_seed
              arms:
                - variant: a
                  weight: 0.5
                - variant: b
                  weight: 0.5
            - name: test_segment_2
              population:
                type: explicit
                value:
                  - id_1
                  - id_2
                  - id_3
                  - id_4
              arms:
                - variant: a
                  weight: 1.0
            - name: test_segment_3
              population:
                type: percent
                value: 0.5
                seed: third_seed
                field: $non_standard_id
              arms:
                - b
                - "off"
        """,
    },
    # Gate with custom field in explicit population
    "custom_explicit": {
        "feature": Feature(
            name="custom_explicit",
            variants=[
                Variant("a", "A"),
                Variant("b", "B"),
                Variant("off", None),
            ],
            default_arm=Arm("off"),
            rollouts=[
                Rollout(
                    name="test_segment_1",
                    population=Population.Explicit(
                        ["id_1", "id_2", "id_3", "id_4"], id_field=_Field("custom")
                    ),
                    arms=[Arm("a", weight=1.0)],
                ),
            ],
        ),
        "yaml": """
        feature:
          name: custom_explicit
          variants:
            a: 'A'
            b: 'B'
            "off": null
          default_arm: "off"
          rollouts:
            - name: test_segment_1
              population:
                type: explicit
                value:
                  - id_1
                  - id_2
                  - id_3
                  - id_4
                field: $custom
              arms:
                - variant: a
                  weight: 1.0
        """,
    },
    # Gate with custom expression in the explicit population field
    "custom_explicit_expression": {
        "feature": Feature(
            name="custom_explicit_expression",
            variants=[
                Variant("a", "A"),
                Variant("b", "B"),
                Variant("off", None),
            ],
            default_arm=Arm("off"),
            rollouts=[
                Rollout(
                    name="test_segment_1",
                    population=Population.Explicit(
                        ["id_1", "id_2", "id_3", "id_4"],
                        id_field=TrimPrefix(_Field("custom"), "prefix_"),
                    ),
                    arms=[Arm("a", weight=1.0)],
                ),
            ],
        ),
        "yaml": """
        feature:
          name: custom_explicit_expression
          variants:
            a: 'A'
            b: 'B'
            "off": null
          default_arm: "off"
          rollouts:
            - name: test_segment_1
              population:
                type: explicit
                value:
                  - id_1
                  - id_2
                  - id_3
                  - id_4
                field: TrimPrefix($custom, "prefix_")
              arms:
                - variant: a
                  weight: 1.0
        """,
    },
    # Gate with a custom expression in the population
    "custom_expression": {
        "feature": Feature(
            name="custom_expression",
            variants=[
                Variant("a", "A"),
                Variant("b", "B"),
                Variant("off", None),
            ],
            default_arm=Arm("off"),
            rollouts=[
                Rollout(
                    name="test_segment_1",
                    population=Population.Expression(
                        _Field("id").in_(["id_1", "id_2", "id_3", "id_4"]),
                    ),
                    arms=[Arm("a", weight=1.0)],
                ),
            ],
        ),
        "yaml": """
        feature:
          name: custom_expression
          variants:
            a: 'A'
            b: 'B'
            "off": null
          default_arm: "off"
          rollouts:
            - name: test_segment_1
              population:
                type: expression
                value: $id In ["id_1", "id_2", "id_3", "id_4"]
              arms:
                - variant: a
                  weight: 1.0
        """,
    },
}


class TestParse(unittest.TestCase):
    def assert_feature(self, name, objs):
        parsed = parse.parse_yaml(objs["yaml"])
        expected = objs["feature"]
        actual = parsed[expected.name]
        assert expected == actual, "Expected:\n{}\n\nActual:\n{}\n".format(
            expected.to_dict(), actual.to_dict()
        )

    def test_parse(self):
        for k, v in FIXTURES.items():
            self.assert_feature(k, v)

    def test_merge(self):
        parsed = parse.parse_yaml(
            FIXTURES["simple"]["yaml"],
            default_features={
                "simplest_feature": Feature(
                    "simplest_feature",
                    variants=[Variant("bar", "This will be overridden")],
                    default_arm=Arm("bar"),
                ),
            },
        )

        actual = parsed["simplest_feature"]
        expected = FIXTURES["simple"]["feature"]
        assert expected == actual, "Expected:\n{}\n\nActual:\n{}\n".format(
            expected.to_dict(), actual.to_dict()
        )

    def test_load_config_local(self):
        with tempfile.NamedTemporaryFile("w") as f:
            f.write("teststring")
            f.flush()
            parsed = parse.load_config(f.name)
            assert parsed == "teststring"

    @responses.activate
    def test_load_config_remote(self):
        responses.add(responses.GET, "http://example.com", body="teststring")
        parsed = parse.load_config("http://example.com")
        assert parsed == "teststring"

    @responses.activate
    def test_load_config_remote_auth(self):
        responses.add(
            responses.GET,
            "http://example.com",
            body="teststring",
            match=[matchers.header_matcher({"authorization": "Bearer token"})],
        )
        parsed = parse.load_config("http://example.com", authorization="Bearer token")
        assert parsed == "teststring"

    @responses.activate
    def test_load_config_remote_invalid(self):
        with pytest.raises(Exception) as exc_info:
            responses.add(responses.GET, "http://example.com", status=400)
            parse.load_config("http://example.com")
        assert str(exc_info.value) == "Failed to load config. Got status 400"

    def test_load_config_fn(self):
        parsed = parse.load_config(lambda: "foo")
        assert parsed == "foo"

    def test_load_config_fn_kwargs(self):
        def _loader(*, arg: str) -> str:
            return f"test: {arg}"

        parsed = parse.load_config(_loader, arg="foo")
        assert parsed == "test: foo"
