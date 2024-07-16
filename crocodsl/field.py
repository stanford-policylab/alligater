from .common import get_entity_field_functor
from .func import _Expression


class _Field(_Expression):
    """Get an attribute from the entity."""

    def __init__(self, *names):
        self.names = names

    def __call__(self, *args, log=None, context=None):
        entity = args[0]
        result = entity
        context = context or {}
        for name in self.names:
            result = get_entity_field_functor(result, name, **context)

        self._trace(log, [entity, repr(self)], result)

        return result

    def __repr__(self):
        return ".".join([f"${name}" for name in self.names])


# Field definitions
#
# These are predefined values that describe how to interpret an arbitrary
# entity in an Expression.


ID = _Field("id")
"""Get the "id" attribute from the entity."""
