# -*- coding: utf-8 -*-
from plone.restapi.exceptions import DeserializationError

import json


def json_body(request):
    try:
        data = json.loads(request.get('BODY', '{}'))
    except ValueError:
        raise DeserializationError(
            '[{}] {} (BODY: "{}"): {}'.format(
                request.HTTP_ACCESS_CONTROL_REQUEST_METHOD,
                request.URL,
                request.BODY,
                'No JSON object could be decoded in the HTTP body of the ' +
                'request.'
            )
        )
    if not isinstance(data, dict):
        raise DeserializationError('Malformed body')
    return data
