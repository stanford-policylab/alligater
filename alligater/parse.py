import traceback

import requests
import yaml
from typing import Callable

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader  # type: ignore

from crocodsl import parse as parse_expression

from .arm import Arm
from .common import InvalidConfigError
from .feature import Feature
from .log import log
from .population import Population
from .rollout import Rollout
from .variant import Variant


ConfigSource = str | Callable[[], str]


def _expand_variants(variants):
    """Parse the variants list specified in YAML.

    Args:
        variants - Map of variants from the YAML config

    Returns:
        List of Variants expected by the Feature
    """
    result = []

    if isinstance(variants, dict):
        variants = [{"name": k, "value": v} for k, v in variants.items()]

    if isinstance(variants, list):
        for v in variants:
            value = v["value"]
            if isinstance(value, dict) and "feature" in value and len(value) == 1:
                # If the value is a nested feature, recurse
                args = _expand_feature(value["feature"])
                value = Feature(**args)
            variant = Variant(v["name"], value)
            result.append(variant)
    else:
        raise ValueError("Expected variants to be a list or map")

    return result


def _expand_expression(expression):
    """Parse an expression from string. See `expr` for more info on syntax.

    Args:
        expression - Encoded expression

    Returns:
        Decoded _Expression
    """
    return parse_expression(expression)


def _expand_population(population):
    """Instantiate a Population object from the raw YAML.

    Args:
        population - The population specification. If this is None, no
        population will be returned (which will result in the default
        population being used.

    Returns:
        Instantiated population, if any. In the case of the default population,
        the string `default` can also be used as shorthand.

    Raises:
        NotImplementedError if an unsupported population specification is provided.
    """
    if not population:
        return None

    if isinstance(population, str):
        return population

    t = population["type"].lower()
    if t == "percent":
        kwargs = {}

        if "field" in population:
            kwargs["id_field"] = _expand_expression(population["field"])

        return Population.Percent(population["value"], population["seed"], **kwargs)
    elif t == "expression":
        expr = _expand_expression(population["value"])
        return Population.Expression(expr)
    elif t == "feature":
        expr = _expand_expression(population["where"])
        return Population.Feature(population["name"], expr)
    elif t == "explicit":
        kwargs = {}

        if "field" in population:
            kwargs["id_field"] = _expand_expression(population["field"])

        return Population.Explicit(population["value"], **kwargs)
    else:
        raise NotImplementedError("Unknown population type {}".format(t))


def _expand_arms(arms):
    """Instantiate Arm objects from a list of arms.

    Args:
        arms - list of raw arms from YAML. List items should either be strings
        or dictionaries containing keys `variant` and optionally `weight`.

    Returns:
        List of arms that can be passed to a Rollout for instantiation.

    Raises:
        ValueError when an item is an unexpected type.
    """
    result = [None] * len(arms)

    for i, arm in enumerate(arms):
        if isinstance(arm, dict):
            args = {}

            if "variant" in arm:
                args["variant_name"] = arm["variant"]

            if "variant_name" in arm:
                args["variant_name"] = arm["variant_name"]

            if "weight" in arm:
                args["weight"] = arm["weight"]

            result[i] = Arm(**args)
        elif isinstance(arm, str):
            result[i] = arm
        else:
            raise ValueError("Unexpected type of arm: {}".format(type(arm)))

    return result


def _expand_rollouts(rollouts):
    """Instantiate Rollouts from the raw list.

    Args:
        rollouts - List of rollout dictionaries

    Returns:
        Instantiated Rollout list.
    """
    result = []

    for rollout in rollouts:
        args = rollout.copy()

        if "population" in args:
            args["population"] = _expand_population(args["population"])

        if "arms" in args:
            args["arms"] = _expand_arms(args["arms"])

        if "randomizer" in args:
            args["randomizer"] = _expand_expression(args["randomizer"])

        result.append(Rollout(**args))

    return result


def _expand_default_arm(default_arm):
    """Instantiate an `Arm` from the default_arm option.

    Args:
        default_arm - name of variant to use as the default treatment.

    Returns:
        Instantiated Arm with weight=1.0.
    """
    return Arm(variant_name=default_arm, weight=1.0)


def _expand_feature(feature, default_feature=None):
    """Instantiate a feature from raw YAML.

    Args:
        feature - Dictionary containing feature specification
        default_feature - optional Feature to use as default arguments.

    Returns:
        Instantiated Feature object.
    """
    result = {}
    if default_feature:
        result.update(default_feature.to_dict())

    if "name" in feature:
        if "name" in result and result["name"] != feature["name"]:
            raise ValueError(
                "Names of default feature and YAML feature differ! Got {}, expected {}".format(
                    result["name"], feature["name"]
                )
            )
        result["name"] = feature["name"]

    if "variants" in feature:
        result["variants"] = _expand_variants(feature["variants"])

    if "default_arm" in feature:
        result["default_arm"] = _expand_default_arm(feature["default_arm"])
        # If the new YAML specifies a default arm, make sure to clear out any
        # default rollout specified in the original feature.
        if "rollouts" in result:
            result["rollouts"] = [
                r for r in result["rollouts"] if r["name"] != Rollout.DEFAULT
            ]

    if "rollouts" in feature:
        result["rollouts"] = _expand_rollouts(feature["rollouts"])

    # `type` is extraneous, remove it
    if "type" in result:
        del result["type"]

    name = result.pop("name")
    return Feature(name, **result)


def _parse_feature_yaml_str(s, default_features=None):
    """Parse Features from a YAML string.

    The parsed features will override any default features supplied.

    Args:
        s - YAML string
        default_features - Optional dictionary of predefined features.

    Returns:
        Dictionary of Features.
    """
    result = {}
    if default_features:
        result.update(default_features)

    for doc in yaml.load_all(s, Loader=Loader):
        name = doc["feature"]["name"]
        default = default_features.get(name, None) if default_features else None
        feature = _expand_feature(doc["feature"], default_feature=default)
        result[name] = feature

    return result


def parse_yaml(s, default_features=None, raise_exceptions=False):
    """Load features from the given YAML config.

    The default definitions of these features can be given in
    `default_features`. The YAML lets different deployments override the
    default implementation.

    Args:
        s - YAML config as a string
        default_features - A dictionary containing the default feature
        definitions by name.
        raise_exceptions - Whether to force exceptions to be raised. Exceptions
        will otherwise be swallowed unless there are no default features.

    Returns:
        Dictionary of instantiated features.

    Raises:
        InvalidConfigError - If the config wasn't found and default_args
        was not specified.
    """
    try:
        return _parse_feature_yaml_str(s, default_features=default_features)
    except Exception as e:
        if default_features is None or raise_exceptions:
            raise InvalidConfigError(str(e)) from e
        else:
            log.warning("😖 Failed to load features from YAML: {}".format(e))
            traceback.print_exc()
            return default_features


_allowed_headers = {"authorization", "accept", "content-type"}


def load_config(source: ConfigSource, **kwargs: dict) -> str:
    """Load a string version of the yaml from the given source.

    Source can be either a local file or a remote URL, or a function.

    Args:
        source - Local file path or remote URL or a function that returns a string.

    Kwargs:
        authorization - Value to use for `Authorization` header, e.g.:
                        "Bearer my.access.token" -- only relevant for remote URLs.
        Other kwargs are passed to the function if it's a callable.

    Returns:
        String contents of the file.
    """
    if callable(source):
        return source(**kwargs)
    elif not isinstance(source, str):
        raise ValueError("Expected a string or callable")

    # Load from a remote path if given something that looks like a URL
    if source.startswith("http://") or source.startswith("https://"):
        headers: dict[str, str] = {}
        for k, v in kwargs.items():
            if k.lower() in _allowed_headers:
                headers[k] = str(v)
        r = requests.get(source, headers=headers)
        if r.status_code < 200 or r.status_code >= 300:
            raise RuntimeError(
                "Failed to load config. Got status {}".format(r.status_code)
            )
        return r.text
    else:
        # Assume it was a local file path
        with open(source) as f:
            return f.read()
