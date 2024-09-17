import asyncio
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Union, cast
from datetime import datetime

import alligater.events as events

from .arm import Arm
from .common import NoAssignment, ValidationError, get_uuid, default_now, NowFn
from .log import log as iolog
from .population import Population
from .rollout import Rollout
from .value import CallType, Value

if TYPE_CHECKING:
    from . import Alligater
    from .cache import AssignmentCache
    from .variant import Variant


ExistingAssignment = tuple[str, Any, datetime]
"""An existing variant name / value / ts that has been assigned."""

AsyncAssignmentFetcher = Callable[["Feature", Any], Awaitable[ExistingAssignment]]
"""Fetch assignments asynchronously."""

SyncAssignmentFetcher = Callable[["Feature", Any], ExistingAssignment]
"""Fetch assignments synchronously."""

AssignmentFetcher = Union[AsyncAssignmentFetcher, SyncAssignmentFetcher]
"""Function to fetch existing assignments for a given feature/entity."""


class Feature:
    """A Feature assigns a treatment using an arbitrary set of rules.

    The available treatments are specified as a list of Variants, which
    themselves can include other Features. (When Features are nested like this
    they are automatically evaluated to the leaf Variants.)

    Variant assignment is governed by the rules in the Rollouts. A Rollout
    specifies how to distribute treatments among a Population. The Population
    can be defined using an arbitrary set of selection criteria -- it might
    represent 100% of users, or a randomly-selected 25% of users, or only users
    who fit certain criteria. The Variant that will be assigned to a member
    of the Population is chosen randomly by the weights assigned to the
    Rollout's treatment Arms.

    Multiple Rollouts can be specified. A default Rollout comprised of the
    entire population *must* be specified, to guarantee that every input will
    be assigned a Variant (even if that Variant is something trivial, like
    `None` or "off"). The `default_arm` arg can be used to specify this easily.
    """

    def __init__(
        self,
        name: str,
        variants: Optional[list["Variant"]] = None,
        rollouts: Optional[list[Rollout]] = None,
        default_arm: Optional[Union[str, Arm]] = None,
    ):
        """Create a new feature gate.

        A default Rollout must be provided; a shortcut to do this is to pass
        a default_arm, which will create the default Rollout automatically.

        Args:
            name - The name of the feature
            variants - Full list of Variants that can be returned by this gate.
            rollouts - List of Rollouts.
            default_arm - Optional default Arm to use (only pass this if no
            default Rollout is included in the `rollouts` list). Can either be
            a string name of a variant, or an Arm object. If the weight is
            specified of the Arm, it must be `1.0`.

        Raises:
            ValidationError if the configuration isn't correct.
        """
        self.name = name
        # Store variants as a map for faster lookup
        self.variants = {v.name: v for v in variants or []}
        self.rollouts = rollouts or []

        # Create a default rollout if one was specified
        if default_arm:
            real_default_arm = (
                Arm(default_arm, weight=1.0)
                if isinstance(default_arm, str)
                else cast(Arm, default_arm)
            )

            if real_default_arm.weight is None:
                real_default_arm.weight = 1.0

            default_rollout = Rollout(
                name=Rollout.DEFAULT,
                population=Population.DEFAULT,
                arms=[real_default_arm],
            )
            self.rollouts.append(default_rollout)

        # Make sure the configuration actually makes sense.
        self.validate()

    def validate(self):
        """Ensure the feature configuration makes sense.

        Raises:
            ValidationError - if feature is invalid for any reason.
        """
        # Variants
        if not self.variants:
            raise ValidationError("At least one variant must be defined")
        [v.validate() for v in self.variants.values()]

        # Rollouts
        if not self.rollouts:
            raise ValidationError("At least one rollout needs to be defined.")

        if not any(r.name == Rollout.DEFAULT for r in self.rollouts):
            raise ValidationError(
                "At least one rollout named {} must be defined".format(Rollout.DEFAULT)
            )

        if not self.rollouts[-1].name == Rollout.DEFAULT:
            raise ValidationError(
                "The {} rollout must be the last rollout in the list".format(
                    Rollout.DEFAULT
                )
            )

        [r.validate(self.variants) for r in self.rollouts]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Feature):
            return False

        return all(
            [
                self.name == other.name,
                self.variants == other.variants,
                self.rollouts == other.rollouts,
            ]
        )

    def __repr__(self) -> str:
        return "<Feature name={}>".format(self.name)

    def to_dict(self) -> dict:
        return {
            "type": "Feature",
            "name": self.name,
            "variants": {k: v.to_dict() for k, v in self.variants.items()},
            "rollouts": [r.to_dict() for r in self.rollouts],
        }

    async def __call__(
        self,
        entity: Any,
        log: Optional[events.EventLogger] = None,
        call_id: Optional[str] = None,
        sticky: Optional[AssignmentFetcher] = None,
        assignment_cache: Optional["AssignmentCache"] = None,
        gater: Optional["Alligater"] = None,
        now: NowFn = default_now,
    ) -> Value[Any]:
        """Apply the gate to the given entity.

        Args:
            entity - the entity to gate
            log - logging function
            sticky - optional function to fetch previous assignment
            assignment_cache - optional local cache of assignments. This is
            only checked if `sticky` is also passed. It should be used to
            avoid race conditions.

        Internal Args:
            call_id - the ID of the feature invocation that this call is
                      nested within. This is None if the call is not nested.
            gater - the Alligater instance
            now - function to get the current time

        Returns:
            Variant that the entity should receive and the CallID.

            The CallID can be used for deferred logging invocations.
        """
        nested = call_id is not None
        variant_name = None
        value = None
        ts = None
        source: Optional[str] = None
        if not nested:
            call_id = get_uuid()
            events.EnterGate(log, feature=self, entity=entity, call_id=call_id, now=now)

        events.EnterFeature(log, feature=self, entity=entity, call_id=call_id, now=now)

        if sticky:
            has_assignment = False

            try:
                # Look up the assignment in the local cache first if possible.
                # This avoids race conditions that come from assignment lookups
                # that happen before they are first written to the server.
                cached = None
                if assignment_cache:
                    cached = assignment_cache.get(self, entity)

                if cached:
                    source = "local"
                    variant_name, value, ts = cached
                else:
                    if asyncio.iscoroutinefunction(sticky):
                        variant_name, value, ts = await cast(
                            AsyncAssignmentFetcher, sticky
                        )(self, entity)
                    else:
                        variant_name, value, ts = cast(SyncAssignmentFetcher, sticky)(
                            self, entity
                        )
                    source = "remote"
                has_assignment = True
            except NoAssignment:
                pass
            except Exception as e:
                events.Error(
                    log,
                    message=f"error evaluating sticky assignment {e}",
                    call_id=call_id,
                    now=now,
                )

                # Don't try to swallow exceptions, since it's now ambiguous
                # whether a value was assigned and it could be problematic for
                # an experiment to reassign something. If for the use-case it
                # doesn't matter whether the feature is re-evaluated, then
                # exceptions should be handled in the `sticky` function itself.
                raise
            finally:
                events.StickyAssignment(
                    log,
                    variant=variant_name,
                    value=value,
                    assigned=has_assignment,
                    ts=ts,
                    source=source,
                    call_id=call_id,
                    now=now,
                )
                if has_assignment:
                    events.LeaveFeature(log, value=value, call_id=call_id, now=now)
                    events.LeaveGate(log, value=value, call_id=call_id, now=now)
                    return Value(  # noqa: B012
                        value,
                        variant_name or "",
                        call_id,
                        CallType.EXPOSURE,
                        log=log,
                        now=lambda: cast(datetime, ts),
                    )

        for r in self.rollouts:
            variant_name = await r(
                cast(str, call_id), entity, log=log, gater=gater, now=now
            )
            if variant_name:
                variant = self.variants[variant_name]

                # By default, this assignment will be permanent if we have a
                # function for sticky assignments. This can be overridden at
                # the rollout level, which can specify explicitly whether or
                # not we want the assignment to be permanent.
                is_sticky_assignment = bool(sticky) if r.sticky is None else r.sticky
                if is_sticky_assignment and not sticky:
                    iolog.warning(
                        f"🏒 Rollout {r.name} requests a persistent (sticky) assignment, "
                        "but no sticky assignment fetcher was passed into Alligater. "
                        "This means assignments are probably being written but never read, "
                        "which seems like an error in your code!"
                    )

                events.ChoseVariant(
                    log,
                    variant=variant,
                    sticky=is_sticky_assignment,
                    call_id=call_id,
                    now=now,
                )
                value = await variant(call_id, entity, log=log, gater=gater, now=now)

                events.LeaveFeature(log, value=value, call_id=call_id, now=now)
                if not nested:
                    events.LeaveGate(log, value=value, call_id=call_id, now=now)

                v = Value(
                    value, variant_name, call_id, CallType.ASSIGNMENT, log=log, now=now
                )
                if assignment_cache:
                    assignment_cache.set(self, entity, variant_name, value, v.ts)
                return v

        # This code is probably unreachable since there has to be a default
        # rollout to fall back on. But the feature definitions can be quite
        # complex and I certainly don't know everything.
        events.Error(log, message="no variant found", call_id=call_id, now=now)
        events.LeaveFeature(log, value=None, call_id=call_id, now=now)
        if not nested:
            events.LeaveGate(log, value=None, call_id=call_id, now=now)

        raise RuntimeError("No variant found")
