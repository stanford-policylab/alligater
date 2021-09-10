from .common import ValidationError
import alligater.func as func
import alligater.field as field
import alligater.events as events



class DefaultSelector:
    """Selector for 100% of the population."""

    def validate(self):
        """Ensures configuration is correct. (It is.)"""
        pass

    def __call__(self, entity, log=None):
        """Returns True -- everyone is in the default population!

        Args:
            entity - Entity to test

        Returns:
            Always True
        """
        events.EvaluatePopulation(log, population=self, entity=entity, member=True)
        return True

    def __eq__(self, other):
        if not isinstance(other, DefaultSelector):
            return False

        return True

    def __repr__(self):
        return "<Population default>"

    def to_dict(self):
        return {
                'type': 'Population',
                'name': 'Default',
                }


class ExpressionSelector:
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

    def __call__(self, entity, log=None):
        """Check whether entity belongs to a this population.

        Args:
            entity - The entity to test

        Returns:
            True or False indicating membership in this population.
        """
        result = self.expression(entity, log=log)
        events.EvaluatePopulation(log, population=self, entity=entity, member=result)
        return result

    def __eq__(self, other):
        if not isinstance(other, ExpressionSelector):
            return False

        return self.expression.equivalent(other.expression)

    def __repr__(self):
        return "<Population expression=({})>".format(self.expression)

    def to_dict(self):
        return {
                'type': 'Population',
                'name': 'Expression',
                'expression': self.expression,
                }


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
    Explicit = ExplicitSelector
