from .func import _Expression
from .common import get_entity_field
import alligater.events as events



class _Field(_Expression):
    """Get an attribute from the entity."""
    
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, log=None, call_id=None):
        entity = args[0]
        result = get_entity_field(entity, self.name)

        self._trace(call_id, log, [entity, self.name], result)

        return result

    def __repr__(self):
        return f"${self.name}"



## Field definitions
#
# These are predefined values that describe how to interpret an arbitrary
# entity in an Expression.


ID = _Field("id")
"""Get the "id" attribute from the entity."""
