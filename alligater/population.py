import abc
from typing import TYPE_CHECKING, Any, Optional

import alligater.events as events
import crocodsl.field as field
import crocodsl.func as func

from .common import ValidationError, NowFn, default_now

if TYPE_CHECKING:
    from . import Alligater


class PopulationSelector(abc.ABC):
    @abc.abstractmethod
    def validate(self): ...

    @abc.abstractmethod
    async def __call__(
        self,
        call_id: str,
        entity: Any,
        log: Optional[events.EventLogger],
        gater: Optional["Alligater"],
        now: NowFn = default_now,
    ) -> bool: ...

    @abc.abstractmethod
    def to_dict(self) -> dict: ...


class DefaultSelector(PopulationSelector):
    """Selector for 100% of the population."""

    def validate(self):
        """Ensures configuration is correct. (It is.)"""
        pass

    async def __call__(self, call_id, entity, log=None, gater=None, now=default_now):
        """Returns True -- everyone is in the default population!

        Args:
            call_id - ID of the exposure evaluation call
            entity - Entity to test

        Returns:
            Always True
        """
        events.EvaluatePopulation(
            log,
            population=self,
            entity=entity,
            member=True,
            call_id=call_id,
            now=now,
        )
        return True

    def __eq__(self, other):
        if not isinstance(other, DefaultSelector):
            return False

        return True

    def __repr__(self):
        return "<Population default>"

    def to_dict(self):
        return {
            "type": "Population",
            "name": "Default",
        }


class ExpressionSelector(PopulationSelector):
    """Selector for a segment of a population based on the given Expression."""

    def __init__(self, expression):
        """Create a selector with the given Expression.

        Args:
            expression - Expression to evaluate to test membership
        """
        self.expression = expression

    def validate(self):
        """Ensures configuration makes sense.

        Raises:
            ValidationError - when something is wrong
        """
        self.expression.validate()

    async def __call__(self, call_id, entity, log=None, gater=None, now=default_now):
        """Check whether entity belongs to a this population.

        Args:
            call_id - ID of the exposure evaluation call
            entity - The entity to test

        Returns:
            True or False indicating membership in this population.
        """

        def trace(name, args, result):
            events.EvalFunc(
                log, f=name, args=args, result=result, call_id=call_id, now=now
            )

        result = self.expression(entity, log=trace, context={"now": now})
        events.EvaluatePopulation(
            log, population=self, entity=entity, member=result, call_id=call_id, now=now
        )
        return result

    def __eq__(self, other):
        if not isinstance(other, ExpressionSelector):
            return False

        return self.expression.equivalent(other.expression)

    def __repr__(self):
        return "<Population expression=({})>".format(self.expression)

    def to_dict(self):
        return {
            "type": "Population",
            "name": "Expression",
            "expression": str(self.expression),
        }


class FeatureSelector(ExpressionSelector):
    """Select a population based on a feature of the entity."""

    def __init__(self, feature, expr):
        """Select a population based on another feature.

        Args:
            feature - Feature to delegate to
            expr - Expression on feature evaluation. $variant, $value, and $assigned are
            variables available for conditioning.
        """
        self.feature = feature
        super().__init__(expr)

    async def __call__(self, call_id, entity, log=None, gater=None, now=default_now):
        """Check whether entity belongs to a this population.

        Args:
            call_id - ID of the exposure evaluation call
            entity - The entity to test

        Returns:
            True or False indicating membership in this population.
        """
        # NOTE: only assignments get logged from this sub-evaluation, never
        # any exposures. In theory the parent exposure should be logged in
        # lieu of the child.
        value = await getattr(gater, self.feature)(entity, deferred=True, now=now)
        result_entity = {
            "value": value.value,
            "variant": value.variant,
            "assigned": value.ts,
        }
        return await super().__call__(
            call_id, result_entity, log=log, gater=gater, now=now
        )


class PercentSelector(ExpressionSelector):
    """Select a percentage of the population."""

    def __init__(self, percent, seed, id_field=field.ID):
        """Select a percentage of the population.

        Args:
            percent - Value in [0, 1] representing % to select.
            seed - Seed to use for randomization. This functions as the salt
            of the hash for reproducible assignments.
            id_field - Field of the Entity to use for hashing.
        """
        self.percent = percent
        expression = func.Hash(func.Concat(seed, id_field)) <= percent
        super().__init__(expression)

    def validate(self):
        """Ensures configuration makes sense.

        Raises:
            ValidationError - when config doesn't make sense
        """
        if self.percent < 0.0:
            raise ValidationError("PercentSelector has to have a positive value")

        if self.percent > 1.0:
            raise ValidationError("PercentSelector has to be less than 1.0")


class ExplicitSelector(ExpressionSelector):
    """Select specific individuals from the population."""

    def __init__(self, ids, id_field=field.ID):
        """Select an explicit set of IDs.

        Args:
            ids - iterable of IDs
            id_field - Field to use as the ID field of the entity
        """
        self.ids = ids
        expression = id_field.in_(ids)
        super().__init__(expression)


class Population:
    """Predefined populations."""

    DEFAULT = DefaultSelector()
    Percent = PercentSelector
    Expression = ExpressionSelector
    Feature = FeatureSelector
    Explicit = ExplicitSelector
