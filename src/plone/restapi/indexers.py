# XXX: EXPERIMENTAL!!!
# This is an experimental feature meant for use in Volto only!
# This code is likely to change in the future, even within minor releases.
# We will make sure plone.restapi latest always works with the latest Volto release.
# This code is planned to being refactored into plone.volto before CMFPlone 6.0 is out.
# <tisto@plone.org>

from plone.app.contenttypes.indexers import SearchableText
from plone.indexer.decorator import indexer
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockSearchableText
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


def _extract_text(block):
    result = ""
    for paragraph in block.get("text", {}).get("blocks", {}):
        text = paragraph["text"]
        result = " ".join((result, text))
    return result


@implementer(IBlockSearchableText)
@adapter(IBlocks, IBrowserRequest)
class TextBlockSearchableText:
    """Searchable Text indexer for Text (DraftJS) blocks."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        return _extract_text(value)


@implementer(IBlockSearchableText)
@adapter(IBlocks, IBrowserRequest)
class TableBlockSearchableText:
    """Searchable Text indexer for Table blocks."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        table = value.get("table", {})
        if not table:
            return ""
        result = ""
        for row in table.get("rows", []):
            for cell in row.get("cells", []):
                for paragraph in cell.get("value", {}).get("blocks", {}):
                    text = paragraph["text"]
                    result = " ".join((result, text))
        return result


@implementer(IBlockSearchableText)
@adapter(IBlocks, IBrowserRequest)
class SlateTextIndexer:
    """Searchable Text indexer for Slate blocks."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        block = block or {}
        # BBB compatibility with slate blocks that used the "plaintext" field
        return block.get("plaintext", "")


@indexer(IBlocks)
def SearchableText_blocks(obj):
    """Extract text to be used by the SearchableText index in the Catalog."""
    request = getRequest()
    blocks = obj.blocks
    blocks_layout = obj.blocks_layout
    blocks_text = []
    for block_id in blocks_layout.get("items", []):
        block = blocks.get(block_id, {})
        # searchableText is the conventional way of storing
        # searchable info in a block
        searchableText = block.get("searchableText", "")
        if searchableText:
            # TODO: should we evaluate in some way this value? maybe passing
            # it into html/plain text transformer?
            blocks_text.append(searchableText)
        else:
            # Use server side adapters to extract the text data
            block_type = block.get("@type", "")
            adapter = queryMultiAdapter(
                (obj, request), IBlockSearchableText, name=block_type
            )
            text = adapter(block) if adapter is not None else ""
            if text:
                blocks_text.append(text)

    # Extract text using the base plone.app.contenttypes indexer
    std_text = SearchableText(obj)
    blocks_text.append(std_text)
    return " ".join(blocks_text)
