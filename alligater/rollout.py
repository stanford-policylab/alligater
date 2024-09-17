from typing import TYPE_CHECKING, Any, Optional, Sequence, Union, cast

import alligater.events as events
import crocodsl.field as field
import crocodsl.func as func

from .arm import Arm
from .common import ValidationError, NowFn, default_now
from .population import Population, PopulationSelector

if TYPE_CHECKING:
    from . import Alligater


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

    def __init__(
        self,
        name: str = DEFAULT,
        population: Union[PopulationSelector, str] = Population.DEFAULT,
        arms: Optional[Sequence[Union[str, Arm]]] = None,
        randomizer: Union[str, func._Expression] = DEFAULT_RANDOMIZER,
        sticky: Optional[bool] = None,
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
        self.sticky = sticky

    def _get_population(
        self, population: Union[PopulationSelector, str]
    ) -> PopulationSelector:
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

        if isinstance(population, str):
            if population.lower() == "default":
                return Population.DEFAULT
            raise ValueError("Invalid population name {}".format(population))

        # Guaranteed to be a real population at this point, not a string
        return cast(PopulationSelector, population)

    def _get_arms(self, arms: Optional[Sequence[Union[str, Arm]]]) -> list[Arm]:
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
        temp_result: list[Optional[Arm]] = [None] * len(arms)

        for i, arm in enumerate(arms):
            if isinstance(arm, str):
                temp_result[i] = Arm(arm)
            elif isinstance(arm, Arm):
                temp_result[i] = arm
                weight = arm.weight
                if weight is not None:
                    remainder -= weight
                    unknown -= 1
            else:
                raise ValueError("Unexpected type for arm: {}".format(type(arm)))

        # All slots are guaranteed to be filled at this point.
        result = cast(list[Arm], temp_result)

        # Divide remaining weight evenly among the unspecified arms.
        unk_weight = remainder / float(unknown) if unknown > 0 else 0.0

        # Fill in any unspecified weights
        for arm in result:
            if arm.weight is None:
                arm.weight = unk_weight

        return result

    def _get_randomizer(
        self, randomizer: Union[str, func._Expression]
    ) -> func._Expression:
        """Get the randomization function to use.

        Args:
            A randomization function or the DEFAULT_RANDOMIZER constant.

        Returns:
            A randomization function
        """
        if isinstance(randomizer, str):
            if randomizer == self.DEFAULT_RANDOMIZER:
                return func.Hash(func.Concat(self.name, ":", field.ID))
            raise ValueError(f"Unknown randomizer {randomizer}")
        return cast(func._Expression, randomizer)

    def validate(self, variants: dict[str, Any]):
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
                raise ValidationError(
                    "Arm refers to unexpected variant `{}`".format(arm.variant_name)
                )
            arm.validate()
            weights += arm.weight

        if weights != 1.0:
            raise ValidationError(
                "Arm weights of rollout must sum to 1.0 (got {0:.2f})".format(weights)
            )

        # Population
        if not self.population:
            raise ValidationError("Missing population in Rollout {}".format(self.name))

        self.population.validate()

        # Special validation for the default rollout. It has to be "complete."
        # In other words, it has to assign literally everyone to some variant.
        if self.name == Rollout.DEFAULT:
            if self.population != Population.DEFAULT:
                raise ValidationError(
                    "The default Rollout must use the default Population"
                )

        if not callable(self.randomize):
            raise ValidationError("Expected randomization function to be callable")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Rollout):
            return False

        return all(
            [
                self.name == other.name,
                self.population == other.population,
                self.arms == other.arms,
                self.randomize == other.randomize,
                self.sticky == other.sticky,
            ]
        )

    def __repr__(self) -> str:
        return "<Rollout name={}>".format(self.name)

    def to_dict(self) -> dict:
        return {
            "type": "Rollout",
            "name": self.name,
            "arms": [a.to_dict() for a in self.arms],
            "population": self.population.to_dict(),
            "randomizer": str(self.randomize),
            "sticky": self.sticky,
        }

    async def __call__(
        self,
        call_id: str,
        entity: dict,
        log: Optional[events.EventLogger] = None,
        gater: Optional["Alligater"] = None,
        now: NowFn = default_now,
    ) -> Optional[str]:
        """Apply this rollout to the given entity.

        Args:
            See `Feature#__call__`.

        Returns:
            A variant name if one should be applied; otherwise None.
        """
        events.EnterRollout(log, rollout=self, call_id=call_id, now=now)

        if not await self.population(call_id, entity, log=log, gater=gater, now=now):
            events.LeaveRollout(log, member=False, call_id=call_id)
            return None

        def trace(name, args, result):
            events.EvalFunc(
                log, f=name, args=args, result=result, call_id=call_id, now=now
            )

        x = self.randomize(entity, log=trace, context={"now": now})

        events.Randomize(
            log,
            entity=entity,
            function=self.randomize,
            result=x,
            call_id=call_id,
            now=now,
        )

        cutoff = 0.0
        for arm in self.arms:
            cutoff += arm.weight
            events.EnterArm(log, arm=arm, cutoff=cutoff, x=x, call_id=call_id, now=now)
            if x <= cutoff:
                events.LeaveArm(log, matched=True, call_id=call_id, now=now)
                events.LeaveRollout(log, member=True, call_id=call_id, now=now)
                return arm.variant_name
            events.LeaveArm(log, matched=False, call_id=call_id, now=now)

        # This would only happen if something was tinkered with after validation
        raise RuntimeError("Could not find arm for entity")
