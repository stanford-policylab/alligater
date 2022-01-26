import unittest
import threading
import time
from unittest.mock import patch
from dataclasses import dataclass
from datetime import datetime

from .log import ObjectLogger
from .feature import Feature
from .variant import Variant



fake_now = datetime(2022, 1, 29, 12, 11, 10, 0)
mock_now = lambda: fake_now


@dataclass
class User:
    id: str


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


class TestObjectLogger(unittest.TestCase):

    @patch('uuid.uuid4', return_value='fakeuuid')
    def test_log_simple(self, uuid4):
        f = Feature(
                'test_feature',
                variants=[Variant('foo', 'Foo')],
                default_arm='foo',
                )

        write = MockWriter()
        f(User("one"), log=ObjectLogger(write, now=mock_now))

        write.assertWritten([{
            'ts': fake_now,
            'call_id': 'fakeuuid',
            'entity': {
                'id': 'one',
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
            'assignment': 'Foo',
            'trace': None,
            }])

    @patch('uuid.uuid4', return_value='fakeuuid')
    def test_log_simple_trace(self, uuid4):
        f = Feature(
                'test_feature',
                variants=[Variant('foo', 'Foo')],
                default_arm='foo',
                )

        write = MockWriter()
        f(User("two"), log=ObjectLogger(write, now=mock_now, trace=True))

        write.assertWritten([{
            'ts': fake_now,
            'call_id': 'fakeuuid',
            'entity': {
                'id': 'two',
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
