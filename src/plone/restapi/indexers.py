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


@implementer(IBlockSearchableText)
@adapter(IBlocks, IBrowserRequest)
class TextBlockSearchableText:
    """Searchable Text indexer for Text (DraftJS) blocks."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        result = ""
        for paragraph in value.get("text", {}).get("blocks", {}):
            text = paragraph["text"]
            result = " ".join((result, text))
        return result


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


def extract_subblocks(block):
    """Extract subblocks from a block.

    :param block: Dictionary with block information.
    :returns: A list with subblocks, if present, or an empty list.
    """
    if "data" in block and "blocks" in block["data"]:
        raw_blocks = block["data"]["blocks"]
    elif "blocks" in block:
        raw_blocks = block["blocks"]
    else:
        raw_blocks = None
    return list(raw_blocks.values()) if isinstance(raw_blocks, dict) else []


def extract_text(block, obj, request):
    """Extract text information from a block.

    This function tries the following methods, until it finds a result:
        1. searchableText attribute
        2. Server side adapter
        3. Subblocks

    The decision to use the server side adapter before the subblocks traversal
    allows addon developers to choose this implementation when they want a
    more granular control of the indexing.

    :param block: Dictionary with block information.
    :param obj: Context to be used to get a IBlockSearchableText.
    :param request: Current request.
    :returns: A string with text found in the block.
    """
    result = ""
    block_type = block.get("@type", "")
    # searchableText is the conventional way of storing
    # searchable info in a block
    searchableText = block.get("searchableText", "")
    if searchableText:
        # TODO: should we evaluate in some way this value? maybe passing
        # it into html/plain text transformer?
        return searchableText
    # Use server side adapters to extract the text data
    adapter = queryMultiAdapter((obj, request), IBlockSearchableText, name=block_type)
    result = adapter(block) if adapter is not None else ""
    if not result:
        subblocks = extract_subblocks(block)
        for subblock in subblocks:
            tmp_result = extract_text(subblock, obj, request)
            result = f"{result}\n{tmp_result}"
    return result


@indexer(IBlocks)
def SearchableText_blocks(obj):
    """Extract text to be used by the SearchableText index in the Catalog."""
    request = getRequest()
    blocks = obj.blocks
    blocks_layout = obj.blocks_layout
    blocks_text = []
    for block_id in blocks_layout.get("items", []):
        block = blocks.get(block_id, {})
        blocks_text.append(extract_text(block, obj, request))

    # Extract text using the base plone.app.contenttypes indexer
    std_text = SearchableText(obj)
    blocks_text.append(std_text)
    return " ".join([text.strip() for text in blocks_text if text.strip()])
