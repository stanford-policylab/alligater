from threading import Lock
from typing import TYPE_CHECKING, Any, Optional, Tuple
from datetime import datetime

if TYPE_CHECKING:
    from .feature import Feature


EntityId = Tuple[str, str]
"""Composite ID of an entity: class name and ID attribute."""

CachedAssignment = Tuple[str, Any, datetime]
"""Cached variant name and value and assignment time."""

AssignmentsCache = dict[str, dict[EntityId, CachedAssignment]]
"""Dictionary containing assignments."""


def _entity_id(entity: Any) -> EntityId:
    """Get the ID from an entity.

    Args:
        entity - Anything with an ID

    Returns:
        Tuple with typename and ID.
    """
    entity_id = None
    if hasattr(entity, "id"):
        entity_id = entity.id
    elif "id" in entity:
        entity_id = entity["id"]
    else:
        entity_id = repr(entity_id)

    return type(entity).__name__, entity_id


class AssignmentCache:
    """Cache feature assignments.

    Currently cache is unbounded since there is the life of the service is not
    long enough for it to matter, but could add TTL.
    """

    def __init__(self):
        self.cache = AssignmentsCache()
        self.lock = Lock()

    def clear(self):
        """Clear the cache."""
        with self.lock:
            self.cache.clear()

    def set(
        self, feature: "Feature", entity: Any, variant: str, value: Any, ts: datetime
    ):
        """Add a new item to the cache.

        Args:
            feature - Feature to look up
            entity - Entity to look up
            variant - Name of variant to set
            value - Value of the variant to set
            ts - Timestamp of the assignment
        """
        with self.lock:
            if feature.name not in self.cache:
                self.cache[feature.name] = {}
            self.cache[feature.name][_entity_id(entity)] = (variant, value, ts)

    def get(self, feature: "Feature", entity: Any) -> Optional[CachedAssignment]:
        """Look up cached assignment.

        Args:
            feature - Feature to look up
            entity - Entity to look up

        Returns:
            Tuple of cached variant name and value and ts, if it exists, or N
        """
        with self.lock:
            return self.cache.get(feature.name, {}).get(_entity_id(entity), None)
