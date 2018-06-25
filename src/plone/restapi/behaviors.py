# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi import _
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import provider

import json


TILES_SCHEMA = json.dumps({
    'type': 'object',
    'properties': {},
})

ARRANGEMENT_SCHEMA = json.dumps({
    'type': 'object',
    'properties': {
        'items': {
            'type': 'array',
            'items': {
                'type': 'string'
            }
        }
    }
})


@provider(IFormFieldProvider)
class ITiles(model.Schema):

    model.fieldset('layout', label=_(u'Layout'),
                   fields=['tiles', 'arrangement'])

    tiles = JSONField(
        title=u'Tiles',
        description=u'The JSON representation of the object tiles information. Must be a JSON object.',  # noqa
        schema=TILES_SCHEMA,
        default={},
        required=False,
    )

    arrangement = JSONField(
        title=u'Arrangement (layout)',
        description=u'The JSON representation of the object tiles arrangement. Must be a JSON array.',  # noqa
        schema=ARRANGEMENT_SCHEMA,
        default={'items': []},
        required=False,
    )
