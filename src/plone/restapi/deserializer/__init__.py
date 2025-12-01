from plone.restapi.exceptions import DeserializationError
from zExceptions import BadRequest

import json


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


def boolean_value(value):
    """

    Args:
        value: a value representing a boolean which can be
               a string, a boolean or an integer
                   (usually a string from a GET parameter).

    Returns: a boolean

    """
    if isinstance(value, bool):
        return value
    if str(value).lower() in ("true", "1"):
        return True
    return False


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
