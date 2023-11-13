from plone.restapi.exceptions import DeserializationError

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
    return value not in {False, "false", "False", "0", 0}
