# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi import _
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import provider

import json


TILES_SCHEMA = json.dumps({"type": "object", "properties": {}})

LAYOUT_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {"items": {"type": "array", "items": {"type": "string"}}},
    }
)


@provider(IFormFieldProvider)
class ITiles(model.Schema):

    model.fieldset("layout", label=_(u"Layout"), fields=["tiles", "tiles_layout"])

    tiles = JSONField(
        title=u"Tiles",
        description=u"The JSON representation of the object tiles information. Must be a JSON object.",  # noqa
        schema=TILES_SCHEMA,
        default={},
        required=False,
    )

    tiles_layout = JSONField(
        title=u"Tiles Layout)",
        description=u"The JSON representation of the object tiles layout. Must be a JSON array.",  # noqa
        schema=LAYOUT_SCHEMA,
        default={"items": []},
        required=False,
    )
