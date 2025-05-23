from plone.app.contenttypes.indexers import SearchableText
from plone.indexer.decorator import indexer
from plone.restapi import HAS_PLONE_6
from plone.restapi.behaviors import IBlocks
from plone.restapi.blocks import visit_subblocks
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
        for subblock in visit_subblocks(obj, block):
            tmp_result = extract_text(subblock, obj, request)
            result = f"{result}\n{tmp_result}"
    return result


def get_blocks_text(obj):
    """Extract text to be used by the SearchableText index in the Catalog."""
    request = getRequest()
    blocks = obj.blocks
    blocks_layout = obj.blocks_layout
    blocks_text = []
    for block_id in blocks_layout.get("items", []):
        block = blocks.get(block_id, {})
        blocks_text.append(extract_text(block, obj, request))
    return blocks_text


def text_strip(text_list):
    return " ".join([text.strip() for text in text_list if text.strip()])


if HAS_PLONE_6:
    # In Plone 6, uses IDynamicTextIndexExtender to index block texts.
    # This ensures that indexing with plone.textindexer continues to work. See:
    # https://github.com/plone/plone.restapi/issues/1744
    from plone.app.dexterity import textindexer

    @implementer(textindexer.IDynamicTextIndexExtender)
    @adapter(IBlocks)
    class BlocksSearchableTextExtender:
        def __init__(self, context):
            self.context = context

        def __call__(self):
            return text_strip(get_blocks_text(self.context))

else:
    # BBB: Plone 5.2 does not have plone.app.dexterity.textindexer.
    # So we need to index with plone.indexer.
    @indexer(IBlocks)
    def SearchableText_blocks(obj):
        blocks_text = get_blocks_text(obj)
        # Extract text using the base plone.app.contenttypes indexer
        std_text = SearchableText(obj)
        blocks_text.append(std_text)
        return text_strip(blocks_text)
