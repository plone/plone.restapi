from typing import Dict, Generator, List, Iterable
from zope.component import adapter
from zope.component import subscribers
from zope.interface import implementer
from zope.interface import Interface
from zope.globalrequest import getRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.restapi.interfaces import IBlockVisitor, IBlockTransformer


def visit_blocks(context, blocks: Dict[str, dict]) -> Generator[dict, None, None]:
    """Visit all blocks, including nested blocks.

    context: Content item where these blocks are stored.
    blocks: A dict mapping block ids to a dict of block data.
    handler: Function to be called for each block found.
    """
    request = getRequest()
    visitors = subscribers((context, request), IBlockVisitor)
    queue: List[dict] = list(blocks.values())
    for block in queue:
        for visitor in visitors:
            queue.extend(visitor(block))
        yield block


def iter_block_transform_handlers(
    context, block_value: dict, interface: IBlockTransformer
) -> Iterable:
    """Find valid handlers for a particular block transformation.

    Looks for adapters of the context and request to this interface.
    Then skips any that are disabled or don't match the block type,
    and returns the remaining handlers sorted by `order`.
    """
    block_type = block_value.get("@type", "")
    handlers = []
    for handler in subscribers((context, getRequest()), interface):
        if handler.block_type == block_type or handler.block_type is None:
            handler.blockid = id
            handlers.append(handler)
    for handler in sorted(handlers, key=lambda h: h.order):
        if not getattr(handler, "disabled", False):
            yield handler


@implementer(IBlockVisitor)
@adapter(Interface, IBrowserRequest)
class NestedBlocksVisitor:
    """Visit nested blocks."""

    def __init__(self, context, request):
        pass

    def __call__(self, block_value: dict):
        """Visit nested blocks in ["data"]["blocks"] or ["blocks"]"""
        if "data" in block_value:
            if isinstance(block_value["data"], dict):
                if "blocks" in block_value["data"]:
                    yield from block_value["data"]["blocks"].values()
        if "blocks" in block_value:
            yield from block_value["blocks"].values()
