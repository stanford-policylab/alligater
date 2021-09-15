from .common import ValidationError



class _EventInstance:
    """Container for event properties.

    The fields available depend on the event.
    """

    def __init__(self, name, **kwargs):
        self.name = name
        self.args = kwargs

    def __str__(self):
        vals = ", ".join([f"{k}={v}" for k, v in self.args.items()])
        return f"[{self.name}] {vals}"

    def __repr__(self):
        return f"<EventInstance {str(self)}>"

    def __getattr__(self, attr):
        try:
            return self.args[attr]
        except KeyError:
            raise AttributeError(attr)

    def __eq__(self, other):
        return self.name == repr(other)


class _Event:
    """An abstract event for building loggers."""

    def __init__(self, name, slots=None):
        self.name = name
        self.slots = slots or []

    def __call__(self, log, **kwargs):
        if not log:
            return

        for slot in self.slots:
            if slot not in kwargs:
                raise ValidationError("Event {} missing slot value for {}".format(self.name, slot))

        instance = _EventInstance(self.name, **kwargs)
        log(instance)

    def __repr__(self):
        return self.name



## Event definitions.
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


ChoseVariant = _Event("ChoseVariant", ("variant",))
"""ChoseVariant is fired when a Variant is selected.

Attributes:
    variant - The Variant that was selected.
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
