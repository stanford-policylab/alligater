import unittest
import tempfile
import time

import responses

from . import Alligater, Feature, Variant



class TestGater(unittest.TestCase):

    def test_no_features(self):
        """Instantiate with no features."""
        gater = Alligater()
        assert gater._features == {}

    def test_no_yaml(self):
        """Instantiate with hardcoded features and no YAML."""
        gater = Alligater(
                features=[
                    Feature('foo', variants=[Variant('foo', 'Foo')], default_arm='foo'),
                    ])
        assert gater.foo({}) == 'Foo'

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
