# Alligater

This is a flexible feature-gating library.

Detailed documentation is in the classes themselves. The quickstart version is:

```py
from alligater import *



# 1. Create the gater withe your list of features.
gater = Alligater(
        features=[
            # This feature will be rolled out randomly to 25% of users.
            Feature(
                'my_feature',
                variants=[
                    Variant('on', True),
                    Variant('off', False),
                    ],
                rollouts=[Rollout(
                  name='my_rollout',
                  population=Population.Percent(0.25, 'seed_value'),
                  arms=['on'],
                  )],
                default_arm='off',
                ),
            ],
        )


# 2. In your code, evaluate your feature when you need to assign a treatment.

# The gater can work for arbitrary objects, but by default it expects that
# the input entity has an `id` attribute or key. This is used for any
# randomization that happens as part of the feature's logic.
some_user = {"id": "id_of_the_user"}

if gater.my_feature(some_user):
    # The feature returned `True` (the `on` variant) for this user!
    # Apply that logic here.
    ...
else:
    # The gate returned `False` (the `off` variant).
    ...
```

## Features:

1. Create any number of features with any number of treatment options.
2. Hierarchical feature definitions. Treatments can be other features. These are evaluated recursively.
3. Load feature definitions from YAML.
4. Flexible targetting. features can target multiple populations with arbitrarily complex logic, assigning treatments either randomly or explicitly.
5. Stable assignments. Choices (even random ones) made by the gater are deterministic.
6. Robust logging. Assignment choices can be inspected in detail with trace logging. The "state of the world" can also be logged as needed for experiment analysis.

Read the class documentation for more info!

## To-do:

It's mostly feature complete, but there are two notable limitations:

- [ ] Expression can't fully be parsed from YAML configs yet.
- [ ] Most Expressions don't currently emit `EvalFunc` trace events yet.
