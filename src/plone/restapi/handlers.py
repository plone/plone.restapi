# coding=ascii

from .interfaces import IBlockTransformer
from plone import api
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest


def transform_blocks(obj, event):
    request = getRequest()

    blocks = obj.blocks

    for id, block in blocks.items():
        transformer = queryMultiAdapter(
            [obj, request], IBlockTransformer, name=block.get('@type', ''))

        if transformer is not None:
            blocks[id] = transformer.transform(block, event=event)
        else:
            blocks[id] = block


class HTMLBlockCleanup(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def transform(self, block_value, event=None):
        portal_transforms = api.portal.get_tool(name='portal_transforms')
        raw_html = block_value.get('html', '')
        data = portal_transforms.convertTo('text/x-html-safe', raw_html,
                                           mimetype="text/html")
        html = data.getData()
        block_value['html'] = html

        return block_value
