from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi import _
from plone.restapi import HAS_PLONE_6
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import provider

import json


try:
    from plone.app.dexterity.textindexer.behavior import IDexterityTextIndexer
except ImportError:
    # BBB: Plone 5.2 does not have plone.app.dexterity.textindexer.
    pass

BLOCKS_SCHEMA = json.dumps({"type": "object", "properties": {}})

LAYOUT_SCHEMA = json.dumps(
    {
        "type": "object",
        "properties": {"items": {"type": "array", "items": {"type": "string"}}},
    }
)


class IBaseBloks(model.Schema):

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


if HAS_PLONE_6:

    # Make IBlocks extend IDexterityTextIndexer, makes that enabling blocks
    # implicitly enables the plone.textindexer indexer
    @provider(IFormFieldProvider)
    class IBlocks(IBaseBloks, IDexterityTextIndexer):
        """"""

else:
    # Plone 5.2 does not have plone.app.dexterity.textindexer.
    # In Plone 5.2 Searchabletext indexing is done with plone.indexer.
    @provider(IFormFieldProvider)
    class IBlocks(IBaseBloks):
        """"""


class IBlocksEditableLayout(IBlocks):
    """Volto Blocks Editable Layout marker interface"""
