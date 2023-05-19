import asyncio
import tempfile
import time
import unittest
from unittest.mock import Mock, call

import responses

from . import Alligater, DeferrableLogger, Feature, NoAssignment, Variant


class MockDeferredLogger(DeferrableLogger):
    def __init__(self):
        self.mock = Mock()

    def __call__(self, *args, **kwargs):
        self.mock(*args, **kwargs)

    def write_log(self, call_id, extra=None):
        self.mock.write_log(call_id, extra=extra)

    def drop_log(self, call_id):
        self.mock.drop_log(call_id)


class TestGater(unittest.IsolatedAsyncioTestCase):
    def test_no_features(self):
        """Instantiate with no features."""
        gater = Alligater()
        assert gater._features == {}

    async def test_no_yaml(self):
        """Instantiate with hardcoded features and no YAML."""
        logger = MockDeferredLogger()
        gater = Alligater(
            logger=logger,
            features=[
                Feature("foo", variants=[Variant("foo", "Foo")], default_arm="foo"),
            ],
        )
        assert await gater.foo({}) == "Foo"
        assert logger.mock.write_log.call_count == 2

    async def test_local_assignment_cache(self):
        def _sticky(feature, entity):
            raise NoAssignment

        foo = Feature(
            "foo",
            variants=[Variant("foo", "Foo"), Variant("bar", "Bar")],
            default_arm="foo",
        )

        gater = Alligater(features=[foo], sticky=_sticky)
        gater._local_assignments.set(foo, {"id": "a"}, "bar", "Bar")
        assert await gater.foo({"id": "a"}) == "Bar"
        assert await gater.foo({"id": "b"}) == "Foo"
        assert gater._local_assignments.get(foo, {"id": "b"}) == ("foo", "Foo")
        gater._local_assignments.clear()
        assert await gater.foo({"id": "a"}) == "Foo"

    async def test_deferred_exposure_logging(self):
        def _sticky(feature, entity):
            if entity["id"] == 2:
                return "bar", "Bar"
            raise NoAssignment

        logger = MockDeferredLogger()
        gater = Alligater(
            logger=logger,
            sticky=_sticky,
            features=[
                Feature("foo", variants=[Variant("foo", "Foo")], default_arm="foo"),
            ],
        )
        v = await gater.foo({"id": 1}, deferred=True)
        assert v == "Foo"
        logger.mock.write_log.has_calls([call("e3e70682-c209-4cac-629f-6fbed82c07cd")])
        assert logger.mock.write_log.call_count == 1
        logger.mock.drop_log.assert_not_called()
        v.log()
        logger.mock.write_log.has_calls(
            [call("e3e70682-c209-4cac-629f-6fbed82c07cd")] * 2
        )
        logger.mock.drop_log.assert_not_called()

        logger.mock.reset_mock()
        v2 = await gater.foo({"id": 2}, deferred=True)
        assert v2 == "Bar"
        logger.mock.write_log.assert_not_called()
        logger.mock.drop_log.assert_not_called()
        call_id = v2._call_id
        v2.log()
        logger.mock.write_log.assert_called_with(call_id, extra=None)
        logger.mock.drop_log.assert_not_called()

    async def test_drop_deferred_logging(self):
        logger = MockDeferredLogger()
        gater = Alligater(
            sticky=lambda x, y: ("foo", "Foo"),
            logger=logger,
            features=[
                Feature("foo", variants=[Variant("foo", "Foo")], default_arm="foo"),
            ],
        )
        v = await gater.foo({}, deferred=True)
        assert v == "Foo"
        call_id = v._call_id
        logger.mock.write_log.assert_not_called()
        logger.mock.drop_log.assert_not_called()
        del v
        logger.mock.write_log.assert_not_called()
        logger.mock.drop_log.assert_called_with(call_id)

    async def test_silence_logging(self):
        """Test that logging can be suppressed."""
        logger = Mock()
        gater = Alligater(
            logger=logger,
            features=[
                Feature("foo", variants=[Variant("foo", "Foo")], default_arm="foo"),
            ],
        )
        assert await gater.foo({}, silent=True) == "Foo"
        logger.assert_not_called()
        assert await gater.foo({}) == "Foo"
        logger.assert_called()

    async def test_yaml_no_reload(self):
        """Instantiate with YAML path and no reload interval."""
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(
                b"""
feature:
  name: simplest_feature
  variants:
    foo: This is the only value
  default_arm: foo
"""
            )
            tf.flush()

            gater = Alligater(yaml=tf.name)

            assert await gater.simplest_feature({}) == "This is the only value"

    async def test_yaml_reload(self):
        """Instantiate with YAML path and reload interval."""
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(
                b"""
feature:
  name: simplest_feature
  variants:
    foo: This is the only value
  default_arm: foo
"""
            )
            tf.flush()

            gater = Alligater(yaml=tf.name, reload_interval=1)
            assert await gater.simplest_feature({}) == "This is the only value"

            tf.write(
                b"""
feature:
  name: simplest_feature
  variants:
    foo: This is no longer the only value
    bar: This is another value
  default_arm: foo
  rollouts:
    - name: new_segment
      arms:
        - bar
      population:
        type: explicit
        value:
          - id_2

---
feature:
  name: another_feature
  variants:
    bar: new feature
  default_arm: bar
"""
            )
            tf.flush()

            time.sleep(2)
            assert (
                await gater.simplest_feature({}) == "This is no longer the only value"
            )
            assert (
                await gater.simplest_feature({"id": "id_2"}) == "This is another value"
            )
            assert await gater.another_feature({}) == "new feature"
            gater.stop()

    @responses.activate
    def test_yaml_remote_config(self):
        """Test with loading remote config."""
        url = "https://policylab.stanford.edu/nudge/config.yaml"
        responses.add(
            responses.GET,
            url,
            body="""
feature:
  name: simplest_feature
  variants:
    foo: This is the only value
  default_arm: foo
""",
        )
        gater = Alligater(yaml=url)
        assert asyncio.run(gater.simplest_feature({})) == "This is the only value"
