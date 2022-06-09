from typing import Any
import collections.abc
import dataclasses
import json
import uuid
from datetime import datetime, date

import mmh3

from .rand import getrandbits



# Maximum value it's possible to represent as a 64-bit double.
MAX_DOUBLE = float(0xFFFFFFFFFFFFFFFF)



def get_uuid() -> str:
    """Get a UUID (v4).

    In tests this can be made deterministic either by patching or seeding the
    random number generator.

    Returns:
        UUIDv4 as a string
    """
    # Call into `random` explicitly so it can be seeded for tests.
    return str(uuid.UUID(int=getrandbits(128)))


def hash_id(s: str) -> float:
    """Compute the hash of the given ID as a float.

    This can be used instead of a PRNG to compute get the effect of random
    assignments without non-determinism from even seeded PRNGs (which would be
    non-deterministic based on call order; assignments would not necessarily
    survive server restarts, for example).

    Args:
        s - string ID representing an arbitrary entity.

    Returns:
        A float in [0, 1] that will always correspond to this entity.
    """
    # Use murmurhash3 to generate the ID. It's faster than cryptographic
    # hashes like MD5, the implementation is somewhat simpler since it
    # generates a float directly, and the output is still uniform.
    #
    # Only using the first half of the full 128-bit number; this is still
    # uniformly distributed and should divide faster. Technique taken from
    # this blog post:
    # https://www.rolando.cl/blog/2018/12/how_uniform_is_md5.html
    return mmh3.hash64(s, signed=False)[0] / MAX_DOUBLE


def is_non_string_iterable(c: Any) -> bool:
    """Check if this is a collection (but not a string).

    Args:
        c - anything
    """
    return isinstance(c, collections.abc.Iterable) and not isinstance(c, str)


def get_entity_field(entity: Any, field_name: str) -> Any:
    """Quietly get a field from an entity.

    Entity can either use dot property access or brackets as a dict.

    Args:
        entity - Entity to evaluate
        field_name - Name of field to get

    Returns:
        Value of field if found, otherwise None
    """
    result = None
    try:
        result = getattr(entity, field_name)
    except AttributeError:
        try:
            result = entity[field_name]
        except Exception:
            pass
    except Exception:
        pass
    return result


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

    if dataclasses.is_dataclass(value):
        d = dataclasses.asdict(value)
        # If a dataclass defins a synthetic `id` using the `@property`
        # decorator, make sure it gets included in the serialization.
        if hasattr(value, 'id'):
            d['id'] = value.id
    elif hasattr(value, 'asdict'):
        d = value.asdict()
    elif hasattr(value, 'to_dict'):
        d = value.to_dict()
    elif hasattr(value, 'to_json'):
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
