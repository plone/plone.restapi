# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_nativestring
from plone.restapi.behaviors import IBlocks
from plone.indexer.decorator import indexer
try:
    from plone.app.contenttypes.indexers import SearchableText
    HAS_PAC = True
except ImportError:
    HAS_PAC = False


def _extract_text(block):
    return " ".join(
        safe_nativestring(paragraph["text"]) for paragraph in block.get("text").get("blocks")
    )


@indexer(IBlocks)
def SearchableText_blocks(obj):
    if not HAS_PAC:
        return ""
    std_text = SearchableText(obj)
    blocks = obj.blocks
    blocks_text = [
        _extract_text(blocks[block_uid])
        for block_uid in obj.blocks
        if blocks[block_uid].get("@type", "") == "text"
    ]
    blocks_text.append(std_text)
    text = " ".join(blocks_text)
    return text
