from plone.restapi.exceptions import DeserializationError
from zExceptions import BadRequest
from zope.deferredimport import deprecated

import json


deprecated(
    "Import from plone.restapi.bbb instead",
    boolean_value="plone.restapi:bbb.boolean_value",
)


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
