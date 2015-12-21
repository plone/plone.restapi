# -*- coding: utf-8 -*-
import json


class DeserializationError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


def json_body(request):
    try:
        data = json.loads(request.get('BODY', '{}'))
    except ValueError:
        raise DeserializationError('No JSON object could be decoded')
    if not isinstance(data, dict):
        raise DeserializationError('Malformed body')
    return data
