import inspect
import sys
from typing import Any
from datetime import datetime, UTC

import mmh3

# Maximum value it's possible to represent as a 64-bit unsigned int, as a float.
MAX_UINT64_F = float(0xFFFFFFFFFFFFFFFF)


def filter_kwargs(f, kwargs):
    """Filter kwargs so that we don't raise the unexpected argument error.

    Args:
        f - function to inspect
        kwargs - args to filter

    Returns:
        Filtered dictionary of kwargs
    """
    sig = inspect.signature(f)
    # If there is a **kwargs argument, pass all the arguments.
    catch_all = any(
        v.kind is inspect.Parameter.VAR_KEYWORD and v.kind.value == 4
        for v in sig.parameters.values()
    )
    return {
        k: v
        for k, v in kwargs.items()
        if catch_all
        or (
            k in sig.parameters
            and sig.parameters[k].kind is not inspect.Parameter.POSITIONAL_ONLY
        )
    }


def dispatch(f, **kwargs):
    """Call a function with dynamic dispatch.

    Args:
        f - function to call
        **kwargs - any arguments to the function

    Returns:
        Result of calling function
    """
    fk = filter_kwargs(f, kwargs)
    return f(**fk)


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


def get_entity_field_functor(obj, prop: str, **kwargs):
    """Functorized `get_entity_field`.

    Look up a property from an object. If the value is callable, the method
    will be called using dynamic dispatch with the given kwargs. Otherwise the
    value will be returned directly.
    The process will be repeated until a non-callable value is returned. An
    error is thrown if a non-callable value is not returned in a reasonable
    number of iterations.

    Args:
        obj - Object to inspect
        prop - Property to get
        **kwargs - Any named args to pass to a method

    Returns:
        Value once all callables have been resolved.

    Raises:
        `RuntimeError` if the functor doesn't produce a simple (non-callable)
        value in a certain number of iterations.
        (The specific value is determined by the global Python max recursion
        limit in `sys`.)
    """
    # Make sure the functor resolves at some point
    i = sys.getrecursionlimit()
    v = get_entity_field(obj, prop)
    while i > 0:
        i -= 1
        if not callable(v):
            return v
        v = dispatch(v, **kwargs)
    else:
        raise RuntimeError("max functor resolution depth reached")


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
    return mmh3.hash64(s, signed=False)[0] / MAX_UINT64_F


def utcnow() -> datetime:
    """Get current timestamp as UTC.

    Returns:
        Timezone-aware UTC timestamp.
    """
    return datetime.now(UTC)
