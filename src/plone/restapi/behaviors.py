from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi import _
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import provider

import json


BLOCKS_SCHEMA = json.dumps({"type": "object", "properties": {}})

LAYOUT_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {"items": {"type": "array", "items": {"type": "string"}}},
    }
)


@provider(IFormFieldProvider)
class IBlocks(model.Schema):

    model.fieldset("layout", label=_("Layout"), fields=["blocks", "blocks_layout"])

    blocks = JSONField(
        title="Blocks",
        description="The JSON representation of the object blocks information. Must be a JSON object.",  # noqa
        schema=BLOCKS_SCHEMA,
        default={},
        required=False,
    )

    blocks_layout = JSONField(
        title="Blocks Layout",
        description="The JSON representation of the object blocks layout. Must be a JSON array.",  # noqa
        schema=LAYOUT_SCHEMA,
        default={"items": []},
        required=False,
    )
