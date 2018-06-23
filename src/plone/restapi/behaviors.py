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
    'type': 'array',
    'items': {
        'type': 'string'
    },
})


@provider(IFormFieldProvider)
class ITiles(model.Schema):

    model.fieldset('layout', label=_(u'Layout'),
                   fields=['tiles', 'arrangement'])

    tiles = JSONField(
        title=u'tiles field',
        schema=TILES_SCHEMA,
        default={},
        required=False,
    )

    arrangement = JSONField(
        title=u'arrangement (layout) field',
        schema=ARRANGEMENT_SCHEMA,
        default=[],
        required=False,
    )
