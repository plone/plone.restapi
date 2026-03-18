from plone.restapi.exceptions import DeserializationError
from zExceptions import BadRequest

import json
import logging


logger = logging.getLogger(__name__)


def json_body(request):
    # TODO We should not read the complete request BODY in memory.
    # Once we have fixed this, we can remove the temporary patches.py.
    # See there for background information.
    try:
        data = json.loads(request.get("BODY") or "{}")
    except ValueError:
        raise DeserializationError("No JSON object could be decoded")
    if not isinstance(data, dict):
        raise DeserializationError("Malformed body")
    return data


def parse_int(data, prop, default):
    """
    Args:
        data: dict from a request
        prop: name of a integer parameter in the dict
        default: default if not found

    Returns: an integer
    Raises: BadRequest if not an int
    """
    try:
        return int(data.get(prop, default))
    except (ValueError, TypeError):
        raise BadRequest(f"Invalid {prop}: Not an integer")


# Backwards compatibility for old Plone versions that do not use plone.base.
# See https://github.com/plone/plone.restapi/issues/1960 and
# https://github.com/plone/plone.base/pull/112
# remove this when we deprecate support for Plone 5.2 and 6.0


def is_truthy(value) -> bool:
    """
    Return `True`, if value is a boolean `True` or an integer `1` or
    a string that looks like "yes", `False` otherwise.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    str_value = str(value).lower().strip()
    return str_value in {
        "1",
        "y",
        "yes",
        "t",
        "true",
        "active",
        "enabled",
        "on",
    }


def is_falsy(value) -> bool:
    """
    Return `True`, if value is a boolean `False` or an integer `0` or
    a string that looks like "no", `False` otherwise.
    """
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value == 0
    str_value = str(value).lower().strip()
    return str_value in {
        "0",
        "n",
        "no",
        "f",
        "false",
        "inactive",
        "disabled",
        "off",
    }


def boolean_value(value, default=None):
    """Return a boolean value for the given input."""
    if is_truthy(value):
        return True
    if is_falsy(value):
        return False
    if default is not None:
        logger.warning(
            "Could not parse value %r as boolean, returning default %r",
            value,
            default,
        )
        return default
    raise ValueError(f"Could not parse value {value!r} as boolean")
