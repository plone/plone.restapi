# -*- coding: utf-8 -*-
from plone.restapi.exceptions import DeserializationError

import json


def json_body(request):
    try:
        data = json.loads(request.get('BODY', '{}'))
    except ValueError:
        raise DeserializationError('No JSON object could be decoded')
    if not isinstance(data, dict):
        raise DeserializationError('Malformed body')
    return data


def boolean_value(value):
    """

    Args:
        value: a value representing a boolean which can be
               a string, a boolean or an integer
                   (usually a string from a GET parameter).

    Returns: a boolean

    """
    return value not in {False, 'false', 'False', '0', 0}
