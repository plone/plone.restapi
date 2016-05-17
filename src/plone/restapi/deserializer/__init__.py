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
