import abc
import inspect
from typing import Any, Optional, Sequence

from .common import ValidationError, simple_object, NowFn, default_now


class EventLogger(abc.ABC):
    """Base class to define a logger."""

    @abc.abstractmethod
    def __call__(self, event: "_EventInstance", now: NowFn = default_now):
        """Log the given event.

        Args:
            event - instantiated event
            now - Function to call to get the current time
        """
        ...


class _EventInstance:
    """Container for event properties.

    The fields available depend on the event.
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.args = kwargs

    def __str__(self):
        vals = ", ".join([f"{k}={v}" for k, v in self.args.items()])
        return f"[{self.name}] {vals}"

    def __repr__(self):
        return f"<EventInstance {str(self)}>"

    def __getattr__(self, attr: str):
        try:
            return self.args[attr]
        except KeyError:
            raise AttributeError(attr)

    def __eq__(self, other):
        return self.name == repr(other)

    def asdict(self, exclude: Optional[dict] = None, compress=False) -> dict:
        """Convert object to a simple dictionary.

        Args:
            exclude - Optional dictionary of redundant fields to exclude
            compress - When serializing, if a key in the data has a `name`
            field, just use that instead of including the whole object. This
            will prevent objects from being excluded entirely, if the `exclude`
            option is also set.

        Returns:
            Dictionary of values
        """
        d: dict[str, Any] = {
            "type": self.name,
            "data": dict[str, Any](),
        }

        for k, v in self.args.items():
            vd = simple_object(v)

            if isinstance(vd, dict) and "name" in vd:
                vd = vd["name"]
            elif exclude and k in exclude and exclude[k] == vd:
                continue

            d["data"][k] = vd

        return d


class _Event:
    """An abstract event for building loggers."""

    def __init__(self, name: str, slots: Optional[Sequence[str]] = None):
        self.name = name
        slots = list(slots or [])
        slots.append("call_id")
        self.slots = tuple(slots)

    def __call__(self, log: Optional[EventLogger], **kwargs):
        if not log:
            return

        for slot in self.slots:
            if slot not in kwargs:
                raise ValidationError(
                    "Event {} missing slot value for {}".format(self.name, slot)
                )

        now_fn = kwargs.pop("now", None)
        instance = _EventInstance(self.name, **kwargs)
        # Assemble args/kwargs for logger.
        log_args: list[Any] = [instance]
        log_kwargs: dict[str, Any] = {}
        # If we have a `now_fn` passed in, see if the logger accepts it.
        # This lets us support our own advanced loggers while keeping
        # backwards-compatibility for using the `print` function.
        if now_fn:
            params = inspect.signature(log).parameters
            if "now" in params:
                log_kwargs["now"] = now_fn
            else:
                ts = now_fn()
                pfx = f"[{ts}]"
                log_args.insert(0, pfx)
        log(*log_args, **log_kwargs)

    def __repr__(self):
        return self.name


# Event definitions.
#
# The following events can be used for building Logging modules to report
# decisions made by the feature gater.


EnterGate = _Event("EnterGate", ("feature", "entity"))
"""EnterGate is fired when the top-level feature begins evaluation.

Attributes:
    feature - The top-level Feature object being evaluated.
    entity - The entity to be assigned.
"""


LeaveGate = _Event("LeaveGate", ("value",))
"""LeaveGate is fired when the top-level feature is finished evaluation.

Attributes:
    value - The value of the assigned Variant.
"""


EnterFeature = _Event("EnterFeature", ("feature", "entity"))
"""EnterFeature is fired when any feature is being evaluated.

It is fired for the top-level feature as well as nested ones.

Attributes:
    feature - The feature being evaluated
    entity - The entity to be assigned
"""


StickyAssignment = _Event(
    "StickyAssignment", ("variant", "value", "assigned", "ts", "source")
)
"""StickyAssignment is fired when the sticky assignment function is evaluated.

Attributes:
    variant - Assigned variant. None if no variant is assigned.
    value - Assigned value. This can be none, which could be a legitimate
    assigned value, or could indicate there was no value assigned yet.
    assigned - Whether or not a value was assigned.
    ts - Timestamp of the assignment.
    source - Source of the assignment ("local" if cached else "remote").
"""


ChoseVariant = _Event(
    "ChoseVariant",
    (
        "variant",
        "sticky",
    ),
)
"""ChoseVariant is fired when a Variant is selected.

Attributes:
    variant - The Variant that was selected.
    sticky - Whether the assignment should be stored permanently.
"""


LeaveFeature = _Event("LeaveFeature", ("value",))
"""LeaveFeature is fired when a feature is finished evaluating.

Fired for top-level as well as nested features.

Attributes:
    value - The vaue of the assigned Variant
"""


EnterRollout = _Event("EnterRollout", ("rollout",))
"""EnterRollout is fired when a Rollout is being evaluated.

Attributes:
    rollout - The rollout being evaluated.
"""


CheckTime = _Event(
    "CheckTime", ("entity", "time_key", "time", "after", "until", "result")
)
"""CheckTime is fired when a time range is being evaluated.

Attributes:
    entity - The entity being evaluated
    time_key - The time key of the entity
    time - The resolved time
    before - Earliest allowable time
    after - Latest allowable time
    result - Whether time was in range
"""


Randomize = _Event("Randomize", ("entity", "function", "result"))
"""Randomize is fired when a coin is being flipped.

Attributes:
    entity - The entity that's being evaluated
    function - The expression being used to flip the coin
    result - The result of flipping the coin in [0, 1]
"""


LeaveRollout = _Event("LeaveRollout", ("member",))
"""LeaveRollout is fired when a Rollout is finished evaluating.

Attributes:
    member - Boolean indicating whether entity was a member of this rollout.
"""


EnterArm = _Event("EnterArm", ("arm", "cutoff", "x"))
"""EnterArm is fired when an Arm is being evaluated.

Attributes:
    arm - The arm being evaluatd
    cutoff - The upper bound of this Arm, in [0, 1]
    x - The hash value of the entity in [0, 1]
"""


LeaveArm = _Event("LeaveArm", ("matched",))
"""LeaveArm is fired when an Arm is finished evaluating.

Attributes:
    matched - Whether the entity is a member of this Arm
"""


EvaluatePopulation = _Event("EvaluatePopulation", ("population", "entity", "member"))
"""EvaluatePopulation is fired when a Population is being evaluated.

Attributes:
    population - The Population definition
    entity - The entity being evaluated
    member - Whether the entity is a member of this Population
"""


EnterVariant = _Event("EnterVariant", ("variant",))
"""EnterVariant is fired when a Variant is being evaluated.

This Variant is the chosen Variant, but it may not be the leaf Variant.

Attributes:
    variant - The Variant definition
"""


VariantRecurse = _Event("VariantRecurse", ("inner",))
"""VariantRecurse is fired when the variant is recursing.

Attributes:
    inner - the callable being recursed into
"""


LeaveVariant = _Event("LeaveVariant", ("value",))
"""LeaveVariant is fired when a Variant is finished evaluating.

Variant might not be the leaf Variant.

Attributes:
    value - The resulting value of this Variant.
"""


EvalFunc = _Event("EvalFunc", ("f", "args", "result"))
"""EvalFunc is fired when an Expression is being evaluated.

This is fired once for every operation in the expression tree.

Attributes:
    f - The name of the function being evaluated
    args - The list of arguments
    result - The evaluation result
"""


Error = _Event("Error", ("message",))
"""Error is emitted when evaluation encounters an unexpected error.

In some cases the exception can be handled internally and is only logged for
visibility; in other cases the exception will be raised as well.

Attributes:
    message - Information about the error
"""
