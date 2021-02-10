# -*- coding: utf-8 -*-
# XXX: EXPERIMENTAL!!!
# This is an experimental feature meant for use in Volto only!
# This code is likely to change in the future, even within minor releases.
# We will make sure plone.restapi latest always works with the latest Volto release.
# This code is planned to being refactored into CMFPlone 6.0 as soon as Volto 4 final is out.
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

import six


def _extract_text(block):
    result = ""
    for paragraph in block.get("text", {}).get("blocks", {}):
        text = paragraph["text"]
        if six.PY2:
            if isinstance(text, six.text_type):
                text = text.encode("utf-8", "replace")
            if text:
                result = " ".join((result, text))
        else:
            result = " ".join((result, text))
    return result


@implementer(IBlockSearchableText)
@adapter(IBlocks, IBrowserRequest)
class TextBlockSearchableText(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        return _extract_text(value)


@indexer(IBlocks)
def SearchableText_blocks(obj):
    request = getRequest()
    blocks = obj.blocks
    blocks_text = []

    for block in blocks.values():

        searchableText = block.get("searchableText", "")
        if searchableText:
            # TODO: should we evaluate in some way this value? maybe passing
            # it into html/plain text transformer?
            blocks_text.append(searchableText)

        block_type = block.get("@type", "")
        adapter = queryMultiAdapter(
            (obj, request), IBlockSearchableText, name=block_type
        )

        if adapter is not None:
            text = adapter(block)

            if text:
                blocks_text.append(text)

    std_text = SearchableText(obj)
    blocks_text.append(std_text)

    return " ".join(blocks_text)
