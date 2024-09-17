import asyncio
from typing import TYPE_CHECKING, Optional

import alligater.events as events

from .common import ValidationError, NowFn, default_now
from .feature import Feature
from .value import Value

if TYPE_CHECKING:
    from . import Alligater


class Variant:
    """A Variant represents a treatment that can be assigned.

    The Variant can store any value whatsoever, identified by a `name` that
    must be a string. This name will be used by `Arm`s to indicate which
    variant to assign.

    The value of a Variant can be another Feature. This creates a
    tree that will be evaluated recursively when the top-level feature gate
    is called.

    The same recursive evaluation can be achieved for other `callable` values
    by setting the `functor` argument to `True`.
    """

    def __init__(self, name, value, functor=False):
        """Create a container for a value to return from the feature gate.

        The value is given a `name` for convenience in logging and debugging.

        If the value is given as a Feature, the Variant will not return the
        value directly, but rather evaluate the Feature recursively. This
        allows for the creation of nested gates. This same behavior can be
        achieved for other callable values by setting `functor=True`.

        Args:
            name - The human-readable label for the variant
            value - Any value to return when the variant is applied
            functor - Whether to treat the `value` as a function that returns
            the true value. (By default this is False; the value will be
            returned literally.) If this is True, the `value` will be called
            with the arguments passed to the Feature call.

        Raises:
            ValidationError - If there's any issue with the configuration
        """
        self.name = name
        self._value = value
        self.is_nested = functor or isinstance(value, Feature)

    def validate(self):
        """Ensure the configuration of this Variant makes sense.

        Raises:
            ValidationError - If there's any issue with the configuration
        """
        if not self.name:
            raise ValidationError("Variant must be given a name")

        if self.is_nested and not callable(self._value):
            raise ValidationError("Expected the value to be callable")

    def __eq__(self, other):
        if not isinstance(other, Variant):
            return False

        return all(
            [
                self.name == other.name,
                self._value == other._value,
                self.is_nested == other.is_nested,
            ]
        )

    def __repr__(self):
        return "<Variant name={}>".format(self.name)

    def to_dict(self):
        v = self._value
        return {
            "type": "Variant",
            "name": self.name,
            "value": v.to_dict() if hasattr(v, "to_dict") else v,
            "nested": self.is_nested,
        }

    async def __call__(
        self,
        call_id,
        entity,
        log=None,
        gater: Optional["Alligater"] = None,
        now: NowFn = default_now,
    ):
        """Get the value for this variant.

        If the value is a Feature (or a `functor`), it will be called with
        all the arguments passed into this function and the result will be
        returned.

        Args:
            See `Feature#__call__`.

        Returns:
            Could be anything.
        """
        events.EnterVariant(log, variant=self, call_id=call_id, now=now)

        if self.is_nested:
            events.VariantRecurse(log, inner=self._value, call_id=call_id, now=now)

            result = None
            if asyncio.iscoroutinefunction(self._value):
                result = await self._value(
                    entity, log=log, call_id=call_id, gater=gater, now=now
                )
            else:
                result = self._value(
                    entity, log=log, call_id=call_id, gater=gater, now=now
                )

            # Unwrap wrapped Values. This happens when features are nested in
            # variants. Only the final value will be wrapped.
            # TODO(jnu): this loses the assignment TS. Unclear if that's expected behavior,
            # but it's something to keep in mind.
            if isinstance(result, Value):
                return result.value
            else:
                return result

        events.LeaveVariant(log, value=self._value, call_id=call_id, now=now)
        return self._value
