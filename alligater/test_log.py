import asyncio
import copy
import json
import threading
import unittest
from dataclasses import dataclass
from datetime import datetime, timezone

import responses

from .arm import Arm
from .common import NoAssignment, SkipLog
from .feature import Feature
from .log import NetworkLogger, ObjectLogger
from .population import Population
from .rollout import Rollout
from .variant import Variant

fake_now = datetime(2022, 1, 29, 12, 11, 10, 0, tzinfo=timezone.utc)


def mock_now():
    return fake_now


mock_url = "https://test.glen/graphql"


@dataclass
class User:
    id: str


def wait_for_responses(logger, timeout=1.0, expected_count=1):
    """Test helper to wait for an NetworkLogger to write something."""
    d = timeout / 4.0
    t = 0.0
    with logger._cv:
        while True:
            assert t < timeout, "Timeout waiting for write"
            if expected_count == 0:
                logger._cv.wait(timeout=d)
                assert len(responses.calls) == 0, "Got unexpected write"
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


class TestObjectLogger(unittest.IsolatedAsyncioTestCase):
    async def test_log_simple(self):
        f = Feature(
            "test_feature",
            variants=[Variant("foo", "Foo")],
            default_arm="foo",
        )

        write = MockWriter()
        v = await f(User("one"), log=ObjectLogger(write), now=mock_now)

        write.assertNotWritten()

        v.log()

        log1 = {
            "ts": fake_now,
            "call_id": "e3e70682-c209-4cac-629f-6fbed82c07cd",
            "entity": {
                "type": "User",
                "value": {
                    "id": "one",
                },
            },
            "feature": {
                "name": "test_feature",
                "rollouts": [
                    {
                        "arms": [
                            {
                                "type": "Arm",
                                "variant": "foo",
                                "weight": 1.0,
                            }
                        ],
                        "name": "default",
                        "population": {
                            "name": "Default",
                            "type": "Population",
                        },
                        "randomizer": "Hash(Concat('default', ':', $id))",
                        "sticky": None,
                        "type": "Rollout",
                    }
                ],
                "type": "Feature",
                "variants": {
                    "foo": {
                        "name": "foo",
                        "nested": False,
                        "type": "Variant",
                        "value": "Foo",
                    },
                },
            },
            "variant": {
                "name": "foo",
                "nested": False,
                "type": "Variant",
                "value": "Foo",
            },
            "assignment": "Foo",
            "repeat": False,
            "trace": None,
            "sticky": False,
        }

        write.assertWritten([log1])

        # Now log an exposure
        v.log()
        log2 = copy.deepcopy(log1)
        log2.update(
            {
                "call_id": log1["call_id"] + ":1",
                "repeat": True,
            }
        )

        write.assertWritten([log1, log2])

    async def test_log_simple_trace(self):
        f = Feature(
            "test_feature",
            variants=[Variant("foo", "Foo")],
            default_arm="foo",
        )

        write = MockWriter()
        v = await f(User("two"), log=ObjectLogger(write, trace=True), now=mock_now)
        v.log()

        write.assertWritten(
            [
                {
                    "ts": fake_now,
                    "call_id": "e3e70682-c209-4cac-629f-6fbed82c07cd",
                    "entity": {
                        "type": "User",
                        "value": {
                            "id": "two",
                        },
                    },
                    "repeat": False,
                    "feature": {
                        "name": "test_feature",
                        "rollouts": [
                            {
                                "arms": [
                                    {
                                        "type": "Arm",
                                        "variant": "foo",
                                        "weight": 1.0,
                                    }
                                ],
                                "name": "default",
                                "population": {
                                    "name": "Default",
                                    "type": "Population",
                                },
                                "randomizer": "Hash(Concat('default', ':', $id))",
                                "sticky": None,
                                "type": "Rollout",
                            }
                        ],
                        "type": "Feature",
                        "variants": {
                            "foo": {
                                "name": "foo",
                                "nested": False,
                                "type": "Variant",
                                "value": "Foo",
                            },
                        },
                    },
                    "variant": {
                        "name": "foo",
                        "nested": False,
                        "type": "Variant",
                        "value": "Foo",
                    },
                    "assignment": "Foo",
                    "sticky": False,
                    "trace": [
                        {"type": "EnterGate", "data": {"feature": "test_feature"}},
                        {"type": "EnterFeature", "data": {"feature": "test_feature"}},
                        {"type": "EnterRollout", "data": {"rollout": "default"}},
                        {
                            "type": "EvaluatePopulation",
                            "data": {
                                "member": True,
                                "population": "Default",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "_Field",
                                "args": [{"id": "two"}, "$id"],
                                "result": "two",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "Concat",
                                "args": ["default", ":", "two"],
                                "result": "default:two",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "Hash",
                                "args": ["default:two"],
                                "result": 0.7560122309797355,
                            },
                        },
                        {
                            "type": "Randomize",
                            "data": {
                                "function": "Hash(Concat('default', ':', $id))",
                                "result": 0.7560122309797355,
                            },
                        },
                        {
                            "type": "EnterArm",
                            "data": {
                                "arm": {"type": "Arm", "variant": "foo", "weight": 1.0},
                                "cutoff": 1.0,
                                "x": 0.7560122309797355,
                            },
                        },
                        {"type": "LeaveArm", "data": {"matched": True}},
                        {"type": "LeaveRollout", "data": {"member": True}},
                        {
                            "type": "ChoseVariant",
                            "data": {"variant": "foo", "sticky": False},
                        },
                        {"type": "EnterVariant", "data": {"variant": "foo"}},
                        {"type": "LeaveVariant", "data": {"value": "Foo"}},
                        {"type": "LeaveFeature", "data": {"value": "Foo"}},
                        {"type": "LeaveGate", "data": {"value": "Foo"}},
                    ],
                }
            ]
        )

    async def test_log_sticky_trace(self):
        f = Feature(
            "test_feature",
            variants=[Variant("foo", "Foo")],
            default_arm="foo",
        )

        mock_assign_ts = datetime(2022, 1, 29, 12, 11, 11, 0, tzinfo=timezone.utc)
        write = MockWriter()
        v = await f(
            User("two"),
            sticky=lambda f, e: ("stickyvariant", "sticky", mock_assign_ts),
            log=ObjectLogger(write, trace=True),
            now=mock_now,
        )
        v.log()

        write.assertWritten(
            [
                {
                    "ts": fake_now,
                    "call_id": "e3e70682-c209-4cac-629f-6fbed82c07cd:1",
                    "entity": {
                        "type": "User",
                        "value": {
                            "id": "two",
                        },
                    },
                    "feature": {
                        "name": "test_feature",
                        "rollouts": [
                            {
                                "arms": [
                                    {
                                        "type": "Arm",
                                        "variant": "foo",
                                        "weight": 1.0,
                                    }
                                ],
                                "name": "default",
                                "population": {
                                    "name": "Default",
                                    "type": "Population",
                                },
                                "randomizer": "Hash(Concat('default', ':', $id))",
                                "sticky": None,
                                "type": "Rollout",
                            }
                        ],
                        "type": "Feature",
                        "variants": {
                            "foo": {
                                "name": "foo",
                                "nested": False,
                                "type": "Variant",
                                "value": "Foo",
                            },
                        },
                    },
                    "repeat": True,
                    "sticky": True,
                    "variant": {"name": "stickyvariant"},
                    "assignment": "sticky",
                    "trace": [
                        {"type": "EnterGate", "data": {"feature": "test_feature"}},
                        {"type": "EnterFeature", "data": {"feature": "test_feature"}},
                        {
                            "type": "StickyAssignment",
                            "data": {
                                "variant": "stickyvariant",
                                "value": "sticky",
                                "assigned": True,
                                "ts": mock_assign_ts.isoformat(),
                                "source": "remote",
                            },
                        },
                        {"type": "LeaveFeature", "data": {"value": "sticky"}},
                        {"type": "LeaveGate", "data": {"value": "sticky"}},
                    ],
                }
            ]
        )

    async def test_log_sticky_trace_new(self):
        """Sticky function is passed but returns nothing in this case."""
        f = Feature(
            "test_feature",
            variants=[Variant("foo", "Foo")],
            default_arm="foo",
        )

        write = MockWriter()

        def sticker(f, e):
            raise NoAssignment

        v = await f(
            User("two"),
            sticky=sticker,
            log=ObjectLogger(write, trace=True),
            now=mock_now,
        )
        v.log()

        write.assertWritten(
            [
                {
                    "ts": fake_now,
                    "call_id": "e3e70682-c209-4cac-629f-6fbed82c07cd",
                    "entity": {
                        "type": "User",
                        "value": {
                            "id": "two",
                        },
                    },
                    "feature": {
                        "name": "test_feature",
                        "rollouts": [
                            {
                                "arms": [
                                    {
                                        "type": "Arm",
                                        "variant": "foo",
                                        "weight": 1.0,
                                    }
                                ],
                                "name": "default",
                                "population": {
                                    "name": "Default",
                                    "type": "Population",
                                },
                                "randomizer": "Hash(Concat('default', ':', $id))",
                                "sticky": None,
                                "type": "Rollout",
                            }
                        ],
                        "type": "Feature",
                        "variants": {
                            "foo": {
                                "name": "foo",
                                "nested": False,
                                "type": "Variant",
                                "value": "Foo",
                            },
                        },
                    },
                    "repeat": False,
                    "sticky": True,
                    "variant": {
                        "name": "foo",
                        "nested": False,
                        "type": "Variant",
                        "value": "Foo",
                    },
                    "assignment": "Foo",
                    "trace": [
                        {"type": "EnterGate", "data": {"feature": "test_feature"}},
                        {"type": "EnterFeature", "data": {"feature": "test_feature"}},
                        {
                            "type": "StickyAssignment",
                            "data": {
                                "variant": None,
                                "value": None,
                                "assigned": False,
                                "ts": None,
                                "source": None,
                            },
                        },
                        {"type": "EnterRollout", "data": {"rollout": "default"}},
                        {
                            "type": "EvaluatePopulation",
                            "data": {
                                "member": True,
                                "population": "Default",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "_Field",
                                "args": [{"id": "two"}, "$id"],
                                "result": "two",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "Concat",
                                "args": ["default", ":", "two"],
                                "result": "default:two",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "Hash",
                                "args": ["default:two"],
                                "result": 0.7560122309797355,
                            },
                        },
                        {
                            "type": "Randomize",
                            "data": {
                                "function": "Hash(Concat('default', ':', $id))",
                                "result": 0.7560122309797355,
                            },
                        },
                        {
                            "type": "EnterArm",
                            "data": {
                                "arm": {"type": "Arm", "variant": "foo", "weight": 1.0},
                                "cutoff": 1.0,
                                "x": 0.7560122309797355,
                            },
                        },
                        {"type": "LeaveArm", "data": {"matched": True}},
                        {"type": "LeaveRollout", "data": {"member": True}},
                        {
                            "type": "ChoseVariant",
                            "data": {"variant": "foo", "sticky": True},
                        },
                        {"type": "EnterVariant", "data": {"variant": "foo"}},
                        {"type": "LeaveVariant", "data": {"value": "Foo"}},
                        {"type": "LeaveFeature", "data": {"value": "Foo"}},
                        {"type": "LeaveGate", "data": {"value": "Foo"}},
                    ],
                }
            ]
        )

    async def test_log_sticky_rollout_override_on(self):
        """Sticky function is not passed, but stipulated by rollout.

        This situation is a little bit fishy, but we technically allow it.
        """
        f = Feature(
            "test_feature",
            variants=[Variant("foo", "Foo")],
            rollouts=[
                Rollout(
                    sticky=True,
                    name=Rollout.DEFAULT,
                    population=Population.DEFAULT,
                    arms=[Arm("foo", weight=1.0)],
                )
            ],
        )

        write = MockWriter()

        v = await f(User("two"), log=ObjectLogger(write, trace=True), now=mock_now)
        v.log()

        write.assertWritten(
            [
                {
                    "ts": fake_now,
                    "call_id": "e3e70682-c209-4cac-629f-6fbed82c07cd",
                    "entity": {
                        "type": "User",
                        "value": {
                            "id": "two",
                        },
                    },
                    "feature": {
                        "name": "test_feature",
                        "rollouts": [
                            {
                                "arms": [
                                    {
                                        "type": "Arm",
                                        "variant": "foo",
                                        "weight": 1.0,
                                    }
                                ],
                                "name": "default",
                                "population": {
                                    "name": "Default",
                                    "type": "Population",
                                },
                                "randomizer": "Hash(Concat('default', ':', $id))",
                                "sticky": True,
                                "type": "Rollout",
                            }
                        ],
                        "type": "Feature",
                        "variants": {
                            "foo": {
                                "name": "foo",
                                "nested": False,
                                "type": "Variant",
                                "value": "Foo",
                            },
                        },
                    },
                    "repeat": False,
                    "sticky": True,
                    "variant": {
                        "name": "foo",
                        "nested": False,
                        "type": "Variant",
                        "value": "Foo",
                    },
                    "assignment": "Foo",
                    "trace": [
                        {"type": "EnterGate", "data": {"feature": "test_feature"}},
                        {"type": "EnterFeature", "data": {"feature": "test_feature"}},
                        {"type": "EnterRollout", "data": {"rollout": "default"}},
                        {
                            "type": "EvaluatePopulation",
                            "data": {
                                "member": True,
                                "population": "Default",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "_Field",
                                "args": [{"id": "two"}, "$id"],
                                "result": "two",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "Concat",
                                "args": ["default", ":", "two"],
                                "result": "default:two",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "Hash",
                                "args": ["default:two"],
                                "result": 0.7560122309797355,
                            },
                        },
                        {
                            "type": "Randomize",
                            "data": {
                                "function": "Hash(Concat('default', ':', $id))",
                                "result": 0.7560122309797355,
                            },
                        },
                        {
                            "type": "EnterArm",
                            "data": {
                                "arm": {"type": "Arm", "variant": "foo", "weight": 1.0},
                                "cutoff": 1.0,
                                "x": 0.7560122309797355,
                            },
                        },
                        {"type": "LeaveArm", "data": {"matched": True}},
                        {"type": "LeaveRollout", "data": {"member": True}},
                        {
                            "type": "ChoseVariant",
                            "data": {"variant": "foo", "sticky": True},
                        },
                        {"type": "EnterVariant", "data": {"variant": "foo"}},
                        {"type": "LeaveVariant", "data": {"value": "Foo"}},
                        {"type": "LeaveFeature", "data": {"value": "Foo"}},
                        {"type": "LeaveGate", "data": {"value": "Foo"}},
                    ],
                }
            ]
        )

    async def test_log_sticky_rollout_override_off(self):
        """Sticky function is passed, but rollout turns it off."""
        f = Feature(
            "test_feature",
            variants=[Variant("foo", "Foo")],
            rollouts=[
                Rollout(
                    sticky=False,
                    name=Rollout.DEFAULT,
                    population=Population.DEFAULT,
                    arms=[Arm("foo", weight=1.0)],
                )
            ],
        )

        write = MockWriter()

        def sticker(f, e):
            raise NoAssignment

        v = await f(
            User("two"),
            sticky=sticker,
            log=ObjectLogger(write, trace=True),
            now=mock_now,
        )
        v.log()

        write.assertWritten(
            [
                {
                    "ts": fake_now,
                    "call_id": "e3e70682-c209-4cac-629f-6fbed82c07cd",
                    "entity": {
                        "type": "User",
                        "value": {
                            "id": "two",
                        },
                    },
                    "feature": {
                        "name": "test_feature",
                        "rollouts": [
                            {
                                "arms": [
                                    {
                                        "type": "Arm",
                                        "variant": "foo",
                                        "weight": 1.0,
                                    }
                                ],
                                "name": "default",
                                "population": {
                                    "name": "Default",
                                    "type": "Population",
                                },
                                "randomizer": "Hash(Concat('default', ':', $id))",
                                "sticky": False,
                                "type": "Rollout",
                            }
                        ],
                        "type": "Feature",
                        "variants": {
                            "foo": {
                                "name": "foo",
                                "nested": False,
                                "type": "Variant",
                                "value": "Foo",
                            },
                        },
                    },
                    "repeat": False,
                    "sticky": False,
                    "variant": {
                        "name": "foo",
                        "nested": False,
                        "type": "Variant",
                        "value": "Foo",
                    },
                    "assignment": "Foo",
                    "trace": [
                        {"type": "EnterGate", "data": {"feature": "test_feature"}},
                        {"type": "EnterFeature", "data": {"feature": "test_feature"}},
                        {
                            "type": "StickyAssignment",
                            "data": {
                                "variant": None,
                                "value": None,
                                "assigned": False,
                                "ts": None,
                                "source": None,
                            },
                        },
                        {"type": "EnterRollout", "data": {"rollout": "default"}},
                        {
                            "type": "EvaluatePopulation",
                            "data": {
                                "member": True,
                                "population": "Default",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "_Field",
                                "args": [{"id": "two"}, "$id"],
                                "result": "two",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "Concat",
                                "args": ["default", ":", "two"],
                                "result": "default:two",
                            },
                        },
                        {
                            "type": "EvalFunc",
                            "data": {
                                "f": "Hash",
                                "args": ["default:two"],
                                "result": 0.7560122309797355,
                            },
                        },
                        {
                            "type": "Randomize",
                            "data": {
                                "function": "Hash(Concat('default', ':', $id))",
                                "result": 0.7560122309797355,
                            },
                        },
                        {
                            "type": "EnterArm",
                            "data": {
                                "arm": {"type": "Arm", "variant": "foo", "weight": 1.0},
                                "cutoff": 1.0,
                                "x": 0.7560122309797355,
                            },
                        },
                        {"type": "LeaveArm", "data": {"matched": True}},
                        {"type": "LeaveRollout", "data": {"member": True}},
                        {
                            "type": "ChoseVariant",
                            "data": {"variant": "foo", "sticky": False},
                        },
                        {"type": "EnterVariant", "data": {"variant": "foo"}},
                        {"type": "LeaveVariant", "data": {"value": "Foo"}},
                        {"type": "LeaveFeature", "data": {"value": "Foo"}},
                        {"type": "LeaveGate", "data": {"value": "Foo"}},
                    ],
                }
            ]
        )


class TestNetworkLogger(unittest.IsolatedAsyncioTestCase):
    @responses.activate
    def test_log_simple(self):
        responses.add(responses.POST, mock_url, json={"data": "ok"})

        f = Feature(
            "test_feature",
            variants=[Variant("foo", "Foo")],
            default_arm="foo",
        )

        logger = NetworkLogger(
            mock_url, headers={"Authorization": "Bearer glen"}, debug=True
        )
        v = asyncio.run(f(User("one"), log=logger, now=mock_now))
        v.log()

        wait_for_responses(logger)

        assert len(responses.calls) == 1
        assert responses.calls[0].request.headers.get("Authorization") == "Bearer glen"
        assert (
            responses.calls[0].request.headers.get("Content-Type")
            == "application/json; charset=utf-8"
        )
        assert json.loads(responses.calls[0].request.body) == {
            "ts": "2022-01-29T12:11:10+00:00",
            "call_id": "e3e70682-c209-4cac-629f-6fbed82c07cd",
            "entity": {
                "type": "User",
                "value": {
                    "id": "one",
                },
            },
            "feature": {
                "name": "test_feature",
                "rollouts": [
                    {
                        "arms": [
                            {
                                "type": "Arm",
                                "variant": "foo",
                                "weight": 1.0,
                            }
                        ],
                        "name": "default",
                        "population": {
                            "name": "Default",
                            "type": "Population",
                        },
                        "randomizer": "Hash(Concat('default', ':', $id))",
                        "sticky": None,
                        "type": "Rollout",
                    }
                ],
                "type": "Feature",
                "variants": {
                    "foo": {
                        "name": "foo",
                        "nested": False,
                        "type": "Variant",
                        "value": "Foo",
                    },
                },
            },
            "variant": {
                "name": "foo",
                "nested": False,
                "type": "Variant",
                "value": "Foo",
            },
            "assignment": "Foo",
            "trace": None,
            "repeat": False,
            "sticky": False,
        }

    @responses.activate
    def test_log_retry(self):
        responses.add(responses.POST, mock_url, status=500)
        responses.add(responses.POST, mock_url, status=500)
        responses.add(responses.POST, mock_url, json={"data": {"id": "mockuid"}})
        logger = NetworkLogger(
            mock_url,
            headers={"Authorization": "Bearer glen"},
            body=lambda x: {"custom": "foo"},
            debug=True,
        )

        f = Feature(
            "test_feature",
            variants=[Variant("foo", "Foo")],
            default_arm="foo",
        )

        v = asyncio.run(f(User("one"), log=logger, now=mock_now))
        v.log()

        wait_for_responses(logger)

        assert len(responses.calls) == 3
        assert responses.calls[0].request.body == '{"custom": "foo"}'

    @responses.activate
    def test_log_format(self):
        responses.add(responses.POST, mock_url, json={"data": {"id": "mockuid"}})

        logger = NetworkLogger(
            mock_url,
            headers={"Authorization": "Bearer glen"},
            body=lambda x: {"custom": "foo"},
            debug=True,
        )

        f = Feature(
            "test_feature",
            variants=[Variant("foo", "Foo")],
            default_arm="foo",
        )

        v = asyncio.run(f(User("one"), log=logger, now=mock_now))
        v.log()

        wait_for_responses(logger)

        assert len(responses.calls) == 1
        assert responses.calls[0].request.body == '{"custom": "foo"}'

    @responses.activate
    def test_log_skip(self):
        def skip_log(x):
            raise SkipLog

        logger = NetworkLogger(
            mock_url,
            headers={"Authorization": "Bearer glen"},
            body=skip_log,
            debug=True,
        )

        f = Feature(
            "test_feature",
            variants=[Variant("foo", "Foo")],
            default_arm="foo",
        )

        v = asyncio.run(f(User("one"), log=logger, now=mock_now))
        v.log()

        wait_for_responses(logger, expected_count=0)

        assert len(responses.calls) == 0
