import collections.abc
import dataclasses
import json
import uuid
from datetime import date, datetime
from typing import Any, Callable

from crocodsl.common import utcnow
from .rand import getrandbits


NowFn = Callable[[], datetime]
"""Function to get the current time."""

default_now: NowFn = utcnow
"""Default function to get the current time."""


def get_uuid() -> str:
    """Get a UUID (v4).

    In tests this can be made deterministic either by patching or seeding the
    random number generator.

    Returns:
        UUIDv4 as a string
    """
    # Call into `random` explicitly so it can be seeded for tests.
    return str(uuid.UUID(int=getrandbits(128)))


def seq_id(current_id: str) -> str:
    """Get a sequential ID based on the current ID.

    This breaks the UUID formatting, but has two advantages:
      - Keeps the provenance of the original event from which
        this event was derived.
      - Can help avoid non-determinism in tests.
    provenance of events based on an original ID.

    Args:
        current_id - Base ID

    Returns:
        Unique ID based on the current ID.
    """
    base_id, _, seq = current_id.partition(":")
    if seq:
        return f"{base_id}:{int(seq) + 1}"
    return f"{base_id}:1"


def is_non_string_iterable(c: Any) -> bool:
    """Check if this is a collection (but not a string).

    Args:
        c - anything
    """
    return isinstance(c, collections.abc.Iterable) and not isinstance(c, str)


def simple_object(value: Any, with_type=False):
    """Try to simplify an arbitrary object to a simple object.

    Args:
        value - Value to simplify
        with_type - Include type information in the object

    Returns:
        Hopefully a simple JSON-type object.
    """
    if is_non_string_iterable(value):
        return [simple_object(v) for v in value]

    d = {}

    # Check if this is a dataclass instance (and not a DataClass type)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        d = dataclasses.asdict(value)
        # If a dataclass defines a synthetic `id` using the `@property`
        # decorator, make sure it gets included in the serialization.
        if hasattr(value, "id"):
            d["id"] = value.id
    elif hasattr(value, "asdict"):
        d = value.asdict()
    elif hasattr(value, "to_dict"):
        d = value.to_dict()
    elif hasattr(value, "to_json"):
        d = value.to_json()
    else:
        d = json.loads(encode_json(value))

    if not with_type:
        return d
    return {
        "type": type(value).__name__,
        "value": d,
    }


def _json_default_encoder(obj: Any) -> str:
    """Default serializer to user with json.dumps.

    Args:
        obj - anything

    Returns:
        A simple JSON type
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


def encode_json(data: Any) -> str:
    """Encode object as json.

    Calls json.dumps with a good serializer.

    Args:
        data - Arbitrary object.

    Returns:
        Encoded string
    """
    return json.dumps(data, sort_keys=True, default=_json_default_encoder)


class ValidationError(Exception):
    """Error to throw when validating features."""

    pass


class InvalidConfigError(Exception):
    """Error thrown when YAML config can't be loaded."""

    pass


class MissingFeatureError(Exception):
    """Error thrown when trying to access an undefined feature."""

    pass


class NoConfig(Exception):
    """Thrown when no YAML config path is provided."""

    pass


class NoReload(Exception):
    """Thrown when no reload interval is given."""

    pass


class LoadError(Exception):
    """Thrown when reloader fails to load YAML."""

    pass


class NoAssignment(Exception):
    """Entity has not been assigned any variant of this feature.

    Throw this in the `sticky` callback to indicate the feature should be
    evaluated because there is no assignment yet.
    """

    pass


class SkipLog(Exception):
    """Raise this exception to prevent logging."""

    pass
