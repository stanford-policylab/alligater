import unittest
from unittest.mock import Mock
import tempfile
import time

import responses

from . import (
        Alligater,
        Feature,
        Variant,
        DeferrableLogger,
        NoAssignment,
        )



class MockDeferredLogger(DeferrableLogger):

    def __init__(self):
        self.mock = Mock()

    def __call__(self, *args, **kwargs):
        self.mock(*args, **kwargs)

    def write_log(self, call_id):
        self.mock.write_log(call_id)

    def drop_log(self, call_id):
        self.mock.drop_log(call_id)


class TestGater(unittest.TestCase):

    def test_no_features(self):
        """Instantiate with no features."""
        gater = Alligater()
        assert gater._features == {}

    def test_no_yaml(self):
        """Instantiate with hardcoded features and no YAML."""
        logger = MockDeferredLogger()
        gater = Alligater(
                logger=logger,
                features=[
                    Feature('foo', variants=[Variant('foo', 'Foo')], default_arm='foo'),
                    ])
        assert gater.foo({}) == 'Foo'
        assert logger.mock.write_log.call_count == 2

    def test_deferred_exposure_logging(self):
        def _sticky(feature, entity):
            if entity['id'] == 2:
                return 'bar', 'Bar'
            raise NoAssignment

        logger = MockDeferredLogger()
        gater = Alligater(
                logger=logger,
                sticky=_sticky,
                features=[
                    Feature('foo', variants=[Variant('foo', 'Foo')], default_arm='foo'),
                    ])
        v = gater.foo({'id': 1}, deferred=True)
        assert v == 'Foo'
        logger.mock.write_log.assert_called_with(v._logged[0])
        assert logger.mock.write_log.call_count == 1
        logger.mock.drop_log.assert_not_called()
        v.log()
        logger.mock.write_log.assert_called_with(v._logged[1])
        logger.mock.drop_log.assert_not_called()

        logger.mock.reset_mock()
        v2 = gater.foo({'id': 2}, deferred=True)
        assert v2 == 'Bar'
        logger.mock.write_log.assert_not_called()
        logger.mock.drop_log.assert_not_called()
        call_id = v2._call_id
        v2.log()
        logger.mock.write_log.assert_called_with(call_id)
        logger.mock.drop_log.assert_not_called()

    def test_drop_deferred_logging(self):
        logger = MockDeferredLogger()
        gater = Alligater(
                sticky=lambda x, y: ('foo', 'Foo'),
                logger=logger,
                features=[
                    Feature('foo', variants=[Variant('foo', 'Foo')], default_arm='foo'),
                    ])
        v = gater.foo({}, deferred=True)
        assert v == 'Foo'
        call_id = v._call_id
        logger.mock.write_log.assert_not_called()
        logger.mock.drop_log.assert_not_called()
        del v
        logger.mock.write_log.assert_not_called()
        logger.mock.drop_log.assert_called_with(call_id)

    def test_silence_logging(self):
        """Test that logging can be suppressed."""
        logger = Mock()
        gater = Alligater(
                logger=logger,
                features=[
                    Feature('foo', variants=[Variant('foo', 'Foo')], default_arm='foo'),
                    ])
        assert gater.foo({}, silent=True) == 'Foo'
        logger.assert_not_called()
        assert gater.foo({}) == 'Foo'
        logger.assert_called()

    def test_yaml_no_reload(self):
        """Instantiate with YAML path and no reload interval."""
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(b"""
feature:
  name: simplest_feature
  variants:
    foo: This is the only value
  default_arm: foo
""")
            tf.flush()

            gater = Alligater(yaml=tf.name)

            assert gater.simplest_feature({}) == 'This is the only value'

    def test_yaml_reload(self):
        """Instantiate with YAML path and reload interval."""
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(b"""
feature:
  name: simplest_feature
  variants:
    foo: This is the only value
  default_arm: foo
""")
            tf.flush()

            gater = Alligater(yaml=tf.name, reload_interval=1)
            assert gater.simplest_feature({}) == 'This is the only value'

            tf.write(b"""
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
""")
            tf.flush()

            time.sleep(2)
            assert gater.simplest_feature({}) == 'This is no longer the only value'
            assert gater.simplest_feature({"id": "id_2"}) == 'This is another value'
            assert gater.another_feature({}) == 'new feature'

    @responses.activate
    def test_yaml_remote_config(self):
        """Test with loading remote config."""
        url = 'https://policylab.stanford.edu/nudge/config.yaml'
        responses.add(responses.GET, url, body="""
feature:
  name: simplest_feature
  variants:
    foo: This is the only value
  default_arm: foo
""")
        gater = Alligater(yaml=url)
        assert gater.simplest_feature({}) == 'This is the only value'
