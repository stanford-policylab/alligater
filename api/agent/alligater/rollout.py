from .common import ValidationError, get_entity_field
from .population import Population
from .arm import Arm
import alligater.field as field
import alligater.func as func
import alligater.events as events



class Rollout:
    """A Rollout describes how to distribute variants to a population.

    Variants are distributed randomly based on a set of weighted Arms to a
    Population that can be any subset of the entire population (including the
    entire population). Membership in the population can be defined with an
    arbitrary set of rules; see `Population` for more details.
    """

    # Name for the default rollout
    DEFAULT = "default"

    # Placeholder to check if the default randomizer should be used.
    DEFAULT_RANDOMIZER = "__default__"

    def __init__(self,
            name=DEFAULT,
            population=Population.DEFAULT,
            arms=None,
            randomizer=DEFAULT_RANDOMIZER,
            ):
        """Construct a new Rollout.

        Args:
            name - Name of the rollout (will use DEFAULT by default)
            population - Population to use for the rollout (by default will
            rollout to everyone using the default population).
            arms - List of Arms to use for choosing treatments. This can be
            either `Arm` objects or strings specifying a Variant name. If the
            weights are missing from the Arms they will be assigned
            automatically by splitting the available space evenly among
            all unspecified arms.
            randomizer - Expression to use to randomize treatment assignment.
            By default this randomizes using the `id` attribute of the input.
        """
        self.name = name
        self.population = self._get_population(population)
        self.arms = self._get_arms(arms)
        self.randomize = self._get_randomizer(randomizer)

    def _get_population(self, population):
        """Get the full population configuration.

        Args:
            population - Usually this should be a Population object. If it's
            not, the string `default` is understood to be the default
            population, as is the value None.

        Returns:
            Instantiated population.

        Raises:
            ValueError if the population is not a recognized value.
        """
        if population is None:
            return Population.DEFAULT

        if type(population) is str:
            if population.lower() == "default":
                return Population.DEFAULT
            raise ValueError("Invalid population name {}".format(population))

        return population

    def _get_arms(self, arms):
        """Get a list of fully-specified arms.

        Since arms can either be a string or an Arm, and the Arm's weight is
        optional, this method will fill in the gaps.

        Specifically, it instantiates strings into Arms, and distributes weight
        evenly where it's unspecified. For example, of the following are
        given:

        ```
        arms=['foo', Arm('bar', weight=0.5)]
        ```

        We will infer the first arm to be `Arm('foo', weight=0.5)`.

        Args:
            arms - list of arms (can be partially specified) as strings or
            Arms, with or without weights.

        Returns:
            List of Arms with computed weights.

        Raises:
            ValueError if arm is neither `str` nor `Arm`.
        """
        if not arms:
            return []

        remainder = 1.0
        unknown = len(arms)
        result = [None] * len(arms)

        for i, arm in enumerate(arms):
            if type(arm) is str:
                result[i] = Arm(arm)
            elif type(arm) is Arm:
                result[i] = arm
                weight = arm.weight
                if weight is not None:
                    remainder -= weight
                    unknown -= 1
            else:
                raise ValueError("Unexpected type for arm: {}".format(type(arm)))

        # Divide remaining weight evenly among the unspecified arms.
        unk_weight = remainder / float(unknown) if unknown > 0 else 0.

        # Fill in any unspecified weights
        for i, arm in enumerate(result):
            if arm.weight is None:
                arm.weight = unk_weight

        return result

    def _get_randomizer(self, randomizer):
        """Get the randomization function to use.

        Args:
            A randomization function or the DEFAULT_RANDOMIZER constant.

        Returns:
            A randomization function
        """
        if randomizer is self.DEFAULT_RANDOMIZER:
            return func.Hash(func.Concat(self.name, ":", field.ID))
        return randomizer

    def validate(self, variants):
        """Ensure configuration makes sense.

        Args:
            variants - dictionary of variants available to the rollout

        Raises:
            ValidationError - if rollout is invalid for any reason
        """
        # Arms
        if not self.arms:
            raise ValidationError("Expected at least one arm")

        weights = 0.0
        for arm in self.arms:
            if arm.variant_name not in variants:
                raise ValidationError("Arm refers to unexpected variant `{}`".format(arm.variant_name))
            arm.validate()
            weights += arm.weight

        if weights != 1.0:
            raise ValidationError("Arm weights of rollout must sum to 1.0 (got {0:.2f})".format(weights))

        # Population
        if not self.population:
            raise ValidationError("Missing population in Rollout {}".format(self.name))

        self.population.validate()

        # Special validation for the default rollout. It has to be "complete."
        # In other words, it has to assign literally everyone to some variant.
        if self.name == Rollout.DEFAULT:
            if self.population != Population.DEFAULT:
                raise ValidationError("The default Rollout must use the default Population")

        if not callable(self.randomize):
            raise ValidationError("Expected randomization function to be callable")

    def __eq__(self, other):
        if not isinstance(other, Rollout):
            return False

        return all([
                self.name == other.name,
                self.population == other.population,
                self.arms == other.arms,
                self.randomize == other.randomize,
                ])

    def __repr__(self):
        return "<Rollout name={}>".format(self.name)

    def to_dict(self):
        return {
                'type': 'Rollout',
                'name': self.name,
                'arms': [a.to_dict() for a in self.arms],
                'population': self.population.to_dict(),
                'randomizer': str(self.randomize),
                }

    def __call__(self, call_id, entity, log=None):
        """Apply this rollout to the given entity.

        Args:
            See `Feature#__call__`.

        Returns:
            A variant name if one should be applied; otherwise None.
        """
        events.EnterRollout(log, rollout=self, call_id=call_id)

        if not self.population(call_id, entity, log=log):
            events.LeaveRollout(log, member=False, call_id=call_id)
            return None

        x = self.randomize(entity, log=log, call_id=call_id)

        events.Randomize(log, entity=entity, function=self.randomize, result=x, call_id=call_id)

        cutoff = 0.0
        for arm in self.arms:
            cutoff += arm.weight
            events.EnterArm(log, arm=arm, cutoff=cutoff, x=x, call_id=call_id)
            if x <= cutoff:
                events.LeaveArm(log, matched=True, call_id=call_id)
                events.LeaveRollout(log, member=True, call_id=call_id)
                return arm.variant_name
            events.LeaveArm(log, matched=False, call_id=call_id)

        # This would only happen if something was tinkered with after validation
        raise RuntimeError("Could not find arm for entity")
