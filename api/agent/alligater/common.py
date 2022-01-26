import collections.abc
import dataclasses
import mmh3



# Maximum value it's possible to represent as a 64-bit double.
MAX_DOUBLE = float(0xFFFFFFFFFFFFFFFF)


def hash_id(s):
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


def is_non_string_iterable(c):
    """Check if this is a collection (but not a string).

    Args:
        c - anything
    """
    return isinstance(c, collections.abc.Iterable) and not isinstance(c, str)


def simple_object(value):
    """Try to simplify an arbitrary object to a simple object.

    Args:
        value - Value to simplify

    Returns:
        Hopefully a simple JSON-type object.
    """
    if is_non_string_iterable(value):
        return [simple_object(v) for v in value]
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    if hasattr(value, 'asdict'):
        return value.asdict()
    elif hasattr(value, 'to_dict'):
        return value.to_dict()
    elif hasattr(value, 'to_json'):
        return value.to_json()
    else:
        # Give up :(
        return value


class ValidationError(Exception):
    """Error to throw when validating features."""
    pass


class InvalidConfigError(Exception):
    """Error thrown when YAML config can't be loaded."""
    pass


class MissingFeatureError(Exception):
    """Error thrown when trying to access an undefined feature."""
    pass
