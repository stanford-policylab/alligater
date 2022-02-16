import unittest
import threading
import time
import responses
import copy
import json
from unittest.mock import patch
from dataclasses import dataclass
from datetime import datetime, timezone

from .log import ObjectLogger, NetworkLogger
from .feature import Feature
from .variant import Variant



fake_now = datetime(2022, 1, 29, 12, 11, 10, 0, tzinfo=timezone.utc)
mock_now = lambda: fake_now

mock_url = "https://test.glen/graphql"


@dataclass
class User:
    id: str


def wait_for_responses(logger, timeout=1., expected_count=1):
    """Test helper to wait for an NetworkLogger to write something."""
    d = timeout / 4.
    t = 0.
    with logger._cv:
        while True:
            assert t < timeout, "Timeout waiting for write"
            if len(responses.calls) < expected_count:
                logger._cv.wait(timeout=d)
                t += d
            else:
                return


class MockWriter:

    def __init__(self):
        self.cv = threading.Condition()
        self.results = []

    def __call__(self, entity):
        with self.cv:
            self.results.append(entity)
            self.cv.notify_all()
    
    def assertWritten(self, expected, timeout=1.0):
        n = 0
        p = timeout / float(len(expected)) if expected else timeout
        with self.cv:
            while len(self.results) < len(expected) and n < timeout:
                self.cv.wait(timeout=p)
                n += p
            assert self.results == expected

    def assertNotWritten(self, timeout=1.0):
        with self.cv:
            self.cv.wait(timeout=timeout)
            assert not self.results


class TestObjectLogger(unittest.TestCase):

    @patch('uuid.uuid4', side_effect=['fakeuuid1', 'fakeuuid2', 'fakeuuid3'])
    def test_log_simple(self, uuid4):
        f = Feature(
                'test_feature',
                variants=[Variant('foo', 'Foo')],
                default_arm='foo',
                )

        write = MockWriter()
        v = f(User("one"), log=ObjectLogger(write, now=mock_now))

        write.assertNotWritten()

        v.log()

        log1 = {
            'ts': fake_now,
            'call_id': 'fakeuuid1',
            'entity': {
                'type': 'User',
                'value': {
                    'id': 'one',
                    },
                },
            'feature': {
                'name': 'test_feature',
                'rollouts': [{
                    'arms': [{
                        'type': 'Arm',
                        'variant': 'foo',
                        'weight': 1.0,
                        }],
                    'name': 'default',
                    'population': {
                        'name': 'Default',
                        'type': 'Population',
                        },
                    'randomizer': "Hash(Concat('default', ':', $id))",
                    'type': 'Rollout',
                    }],
                'type': 'Feature',
                'variants': {
                    'foo': {
                        'name': 'foo',
                        'nested': False,
                        'type': 'Variant',
                        'value': 'Foo',
                        },
                    },
                },
            'variant': {'name': 'foo', 'nested': False, 'type': 'Variant', 'value': 'Foo'},
            'assignment': 'Foo',
            'repeat': False,
            'trace': None,
            }

        write.assertWritten([log1])

        # Now log an exposure
        v.log()
        log2 = copy.deepcopy(log1)
        log2.update({
            'call_id': 'fakeuuid2',
            'repeat': True,
            })

        write.assertWritten([log1, log2])
        assert v._call_id == 'fakeuuid3'

    @patch('uuid.uuid4', side_effect=['fakeuuid1', 'fakeuuid2'])
    def test_log_simple_trace(self, uuid4):
        f = Feature(
                'test_feature',
                variants=[Variant('foo', 'Foo')],
                default_arm='foo',
                )

        write = MockWriter()
        f(User("two"), log=ObjectLogger(write, now=mock_now, trace=True)).log()

        write.assertWritten([{
            'ts': fake_now,
            'call_id': 'fakeuuid1',
            'entity': {
                'type': 'User',
                'value': {
                    'id': 'two',
                    },
                },
            'repeat': False,
            'feature': {
                'name': 'test_feature',
                'rollouts': [{
                    'arms': [{
                        'type': 'Arm',
                        'variant': 'foo',
                        'weight': 1.0,
                        }],
                    'name': 'default',
                    'population': {
                        'name': 'Default',
                        'type': 'Population',
                        },
                    'randomizer': "Hash(Concat('default', ':', $id))",
                    'type': 'Rollout',
                    }],
                'type': 'Feature',
                'variants': {
                    'foo': {
                        'name': 'foo',
                        'nested': False,
                        'type': 'Variant',
                        'value': 'Foo',
                        },
                    },
                },
            'variant': {'name': 'foo', 'nested': False, 'type': 'Variant', 'value': 'Foo'},
            'assignment': 'Foo',
            'trace': [
                {'type': 'EnterGate', 'data': {'feature': 'test_feature'}},
                {'type': 'EnterFeature', 'data': {'feature': 'test_feature'}},
                {'type': 'EnterRollout', 'data': {'rollout': 'default'}},
                {'type': 'EvaluatePopulation', 'data': {
                    'member': True,
                    'population': 'Default',
                    }},
                {'type': 'EvalFunc', 'data': {
                    'f': '_Field',
                    'args': [{'id': 'two'}, 'id'],
                    'result': 'two',
                    }},
                {'type': 'EvalFunc', 'data': {
                    'f': 'Concat',
                    'args': ['default', ':', 'two'],
                    'result': 'default:two',
                    }},
                {'type': 'EvalFunc', 'data': {
                    'f': 'Hash',
                    'args': ['default:two'],
                    'result': 0.7560122309797355,
                    }},
                {'type': 'Randomize', 'data': {
                    'function': "Hash(Concat('default', ':', $id))",
                    'result': 0.7560122309797355,
                    }},
                {'type': 'EnterArm',
                    'data': {
                        'arm': {'type': 'Arm', 'variant': 'foo', 'weight': 1.0},
                        'cutoff': 1.0,
                        'x': 0.7560122309797355,
                        },
                    },
                {'type': 'LeaveArm', 'data': {'matched': True}},
                {'type': 'LeaveRollout', 'data': {'member': True}},
                {'type': 'ChoseVariant', 'data': {'variant': 'foo'}},
                {'type': 'EnterVariant', 'data': {'variant': 'foo'}},
                {'type': 'LeaveVariant', 'data': {'value': 'Foo'}},
                {'type': 'LeaveFeature', 'data': {'value': 'Foo'}},
                {'type': 'LeaveGate', 'data': {'value': 'Foo'}},
                ],
            }])

    @patch('uuid.uuid4', side_effect=['fakeuuid1', 'fakeuuid2'])
    def test_log_sticky_trace(self, uuid4):
        f = Feature(
                'test_feature',
                variants=[Variant('foo', 'Foo')],
                default_arm='foo',
                )

        write = MockWriter()
        f(User("two"),
                sticky=lambda f, e: ('stickyvariant', 'sticky'),
                log=ObjectLogger(write, now=mock_now, trace=True)).log()

        write.assertWritten([{
            'ts': fake_now,
            'call_id': 'fakeuuid1',
            'entity': {
                'type': 'User',
                'value': {
                    'id': 'two',
                    },
                },
            'feature': {
                'name': 'test_feature',
                'rollouts': [{
                    'arms': [{
                        'type': 'Arm',
                        'variant': 'foo',
                        'weight': 1.0,
                        }],
                    'name': 'default',
                    'population': {
                        'name': 'Default',
                        'type': 'Population',
                        },
                    'randomizer': "Hash(Concat('default', ':', $id))",
                    'type': 'Rollout',
                    }],
                'type': 'Feature',
                'variants': {
                    'foo': {
                        'name': 'foo',
                        'nested': False,
                        'type': 'Variant',
                        'value': 'Foo',
                        },
                    },
                },
            'repeat': True,
            'variant': {'name': 'stickyvariant'},
            'assignment': 'sticky',
            'trace': [
                {'type': 'EnterGate', 'data': {'feature': 'test_feature'}},
                {'type': 'EnterFeature', 'data': {'feature': 'test_feature'}},
                {'type': 'StickyAssignment', 'data': {'variant': 'stickyvariant', 'value': 'sticky', 'assigned': True}},
                {'type': 'LeaveFeature', 'data': {'value': 'sticky'}},
                {'type': 'LeaveGate', 'data': {'value': 'sticky'}},
                ],
            }])


class TestNetworkLogger(unittest.TestCase):

    @responses.activate
    @patch('uuid.uuid4', side_effect=['fakeuuid1', 'fakeuuid2'])
    def test_log_simple(self, uuid4):
        responses.add(responses.POST,
                mock_url,
                json={"data": "ok"})

        f = Feature(
                'test_feature',
                variants=[Variant('foo', 'Foo')],
                default_arm='foo',
                )

        logger = NetworkLogger(mock_url,
                headers={'Authorization': 'Bearer glen'},
                now=mock_now,
                debug=True)
        f(User("one"), log=logger).log()

        wait_for_responses(logger)

        assert len(responses.calls) == 1
        assert responses.calls[0].request.headers.get('Authorization') == 'Bearer glen'
        assert responses.calls[0].request.headers.get('Content-Type') == 'application/json; charset=utf-8'
        assert json.loads(responses.calls[0].request.body) == {
            'ts': '2022-01-29T12:11:10+00:00',
            'call_id': 'fakeuuid1',
            'entity': {
                'type': 'User',
                'value': {
                    'id': 'one',
                    },
                },
            'feature': {
                'name': 'test_feature',
                'rollouts': [{
                    'arms': [{
                        'type': 'Arm',
                        'variant': 'foo',
                        'weight': 1.0,
                        }],
                    'name': 'default',
                    'population': {
                        'name': 'Default',
                        'type': 'Population',
                        },
                    'randomizer': "Hash(Concat('default', ':', $id))",
                    'type': 'Rollout',
                    }],
                'type': 'Feature',
                'variants': {
                    'foo': {
                        'name': 'foo',
                        'nested': False,
                        'type': 'Variant',
                        'value': 'Foo',
                        },
                    },
                },
            'variant': {'name': 'foo', 'nested': False, 'type': 'Variant', 'value': 'Foo'},
            'assignment': 'Foo',
            'trace': None,
            'repeat': False,
            }

    @responses.activate
    def test_log_format(self):
        responses.add(responses.POST,
                mock_url,
                status=500)
        responses.add(responses.POST,
                mock_url,
                json={"data": {"id": "mockuid"}})

        logger = NetworkLogger(mock_url,
                headers={'Authorization': 'Bearer glen'},
                now=mock_now,
                body=lambda x: {"custom": "foo"},
                debug=True)

        f = Feature(
                'test_feature',
                variants=[Variant('foo', 'Foo')],
                default_arm='foo',
                )

        f(User("one"), log=logger).log()

        wait_for_responses(logger)

        assert len(responses.calls) == 1
        assert responses.calls[0].request.body == '{"custom": "foo"}'
