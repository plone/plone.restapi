from plone.restapi.exceptions import DeserializationError

import json


def json_body(request):
    bodyfile = request.get("BODYFILE")
    if bodyfile is None:
        data = {}
    else:
        if bodyfile.tell() != 0:
            # Something has already read the bodyfile.
            # Go back to the beginning.
            bodyfile.seek(0)
        try:
            data = json.load(bodyfile)
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
