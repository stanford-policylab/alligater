from functools import partial

from .feature import Feature
from .variant import Variant
from .arm import Arm
from .rollout import Rollout
from .population import Population
from .common import ValidationError
from .parse import parse_yaml
from .log import default_logger
import alligater.func as func
import alligater.field as field



class Alligater:
    """The Alligater object represents the universe of available features.

    The Alligater instance evaluates features to return an assignment. For
    example:

    ```
    gater = Alligater(yaml='path/to/my/features.yaml')

    # Assuming a feature with name "my_feature" was defined in the YAML:
    treatment = gater.my_feature(some_user)
    ```

    The Alligater instance can be configured with different modes of logging
    in order to preserve and/or debug the assignment decisions it makes.
    """

    def __init__(self, features=None, yaml=None, logger=default_logger):
        """Create a new feature gater.

        Features can either come from a hardcoded predefined list or YAML.
        If YAML is specified, it will override the hardcoded list.

        Args:
            features - List or dictionary of features.
            yaml - Path to features specified in YAML.
            logger - Function to call to log decisions. See `events` for more
            information about how to interpret gating decisions.
        """
        self._logger = logger

        if type(features) is list:
            features = {f.name: f for f in features}

        if yaml:
            self._features = parse_yaml(yaml, features=features)
        elif features:
            self._features = features.copy()

        if not self._features:
            raise RuntimeError("No features are defined!")

    def __getattr__(self, feature_name):
        """Get a function that will evaluate the given feature.

        Args:
            feature_name - Name of feature to evaluate

        Returns:
            Function that can be called with an `entity` to evaluate.
        """
        try:
            ft = self._features[feature_name]
            return partial(self, ft)
        except KeyError:
            raise AttributeError(feature_name)

    def __call__(self, feature, entity):
        """Evaluate an entity against the given feature.

        Args:
            feature - Feature to evaluate
            entity - Arbitrary entity to evaluate
        
        Returns:
            Value of the variant to return.
        """
        return feature(entity, log=self._logger)



__all__ = [
        'Alligater',
        'Feature',
        'Variant',
        'Arm',
        'Rollout',
        'Population',
        'ValidationError',
        'func',
        'field',
        'events',
        ]
