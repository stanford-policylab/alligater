import asyncio
import tempfile
import time
import unittest
from unittest.mock import Mock, call
from datetime import datetime, UTC

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

        mock_ts = datetime(2024, 1, 2, 3, 4, 5, tzinfo=UTC)
        mock_ts2 = datetime(2024, 1, 2, 3, 4, 6, tzinfo=UTC)
        gater = Alligater(features=[foo], sticky=_sticky, now=lambda: mock_ts2)
        gater._local_assignments.set(foo, {"id": "a"}, "bar", "Bar", mock_ts)
        assert await gater.foo({"id": "a"}) == "Bar"
        assert await gater.foo({"id": "b"}) == "Foo"
        assert gater._local_assignments.get(foo, {"id": "b"}) == (
            "foo",
            "Foo",
            mock_ts2,
        )
        gater._local_assignments.clear()
        assert await gater.foo({"id": "a"}) == "Foo"

    async def test_deferred_exposure_logging(self):
        def _sticky(feature, entity):
            if entity["id"] == 2:
                return "bar", "Bar", datetime(2024, 1, 2, 3, 4, 5, tzinfo=UTC)
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
        logger.mock.write_log.assert_has_calls(
            [call("e3e70682-c209-4cac-629f-6fbed82c07cd", extra=None)]
        )
        assert logger.mock.write_log.call_count == 1
        logger.mock.drop_log.assert_not_called()
        v.log()
        logger.mock.write_log.assert_has_calls(
            [call("e3e70682-c209-4cac-629f-6fbed82c07cd", extra=None)] * 2
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
            sticky=lambda x, y: (
                "foo",
                "Foo",
                datetime(2024, 1, 2, 3, 4, 5, tzinfo=UTC),
            ),
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

    async def test_cross_ref_features(self):
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(
                b"""
feature:
  name: ft1
  variants:
    var1: a
    var2: b
  rollouts:
    - name: segment1
      arms: [var2]
      population:
        type: explicit
        value: [id_2]
  default_arm: var1

---

feature:
  name: ft2
  variants:
    varX: x
    varY: y
  default_arm: varX
  rollouts:
    - name: segmentZ
      arms: [varY]
      population:
        type: feature
        name: ft1
        where: $value Eq 'b'

---

feature:
  name: ft3
  variants:
    varI: i
    varJ: j
  default_arm: varI
  rollouts:
    - name: segmentK
      arms: [varJ]
      population:
        type: feature
        name: ft1
        where: $variant Eq 'var2'
"""
            )
            tf.flush()

            gater = Alligater(yaml=tf.name, reload_interval=1)
            assert await gater.ft1({"id": "id_1"}) == "a"
            assert await gater.ft1({"id": "id_2"}) == "b"
            assert await gater.ft2({"id": "id_1"}) == "x"
            assert await gater.ft2({"id": "id_2"}) == "y"
            assert await gater.ft3({"id": "id_1"}) == "i"
            assert await gater.ft3({"id": "id_2"}) == "j"
            gater.stop()

    async def test_cross_ref_features_assigned_ts(self):
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(
                b"""
feature:
  name: ft1
  variants:
    var1: a
    var2: b
  rollouts:
    - name: segment1
      arms: [var2]
      sticky: true
      population:
        type: explicit
        value: [id_2]
  default_arm: var1

---

feature:
  name: ft2
  variants:
    var_old: old
    var_new: new
  default_arm: var_old
  rollouts:
    - name: segmentK
      arms: [var_new]
      population:
        type: feature
        name: ft1
        where: TimeSince($assigned, 'mo') Lt 6
"""
            )
            tf.flush()

            mock_assigned_ts = datetime(2023, 1, 2, 3, 4, 5, tzinfo=UTC)
            mock_current_ts = datetime(2023, 8, 2, 3, 4, 6, tzinfo=UTC)

            def _sticky(feature, entity):
                if entity["id"] == "id_2" and feature.name == "ft1":
                    return "var2", "b", mock_assigned_ts
                raise NoAssignment

            gater = Alligater(
                yaml=tf.name,
                reload_interval=1,
                sticky=_sticky,
                now=lambda: mock_current_ts,
            )
            assert await gater.ft1({"id": "id_1"}) == "a"
            assert await gater.ft1({"id": "id_2"}) == "b"
            assert await gater.ft2({"id": "id_1"}) == "new"
            assert await gater.ft2({"id": "id_2"}) == "old"
            gater.stop()

    @responses.activate
    def test_yaml_remote_config(self):
        """Test with loading remote config."""
        url = "https://policylab.hks.harvard.edu/alligater/config.yaml"
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
