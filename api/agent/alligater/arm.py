from .common import ValidationError


class Arm:
    """An Arm represents a treatment group as a proportion of a population.

    The arm specifies a weight, which is a % of its parent population, and the
    name of a variant, which is the treatment this group will receive.
    """

    def __init__(self, variant_name, weight=None):
        """Create a new Arm representing the given variant.

        The weight does not need to be specified initially, but it will need
        to be set before `validate` is called.

        Args:
            variant_name - name of Variant that this Arm represents.
            weight - Optional float weight in [0, 1]
        """
        self.variant_name = variant_name
        self.weight = weight

    def __eq__(self, other):
        if not isinstance(other, Arm):
            return False

        return all(
            [
                self.variant_name == other.variant_name,
                self.weight == other.weight,
            ]
        )

    def __repr__(self):
        return "<Arm name={} weight={}>".format(self.variant_name, self.weight)

    def to_dict(self):
        return {
            "type": "Arm",
            "variant": self.variant_name,
            "weight": self.weight,
        }

    def validate(self):
        """Ensure configuration makes sense.

        Raises:
            ValidationError - if config doesn't make sense
        """
        if self.weight < 0.0:
            raise ValidationError("Arm weight must be positive")
        if self.weight > 1.0:
            raise ValidationError("Arm weight can't be greater than 1.0")
