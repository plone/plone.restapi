from .interfaces import IBlockTransformer
from base64 import b64decode
from plone import api
from plone.dexterity.utils import createContentInContainer
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


class ImageBlockUpload(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def upload_image(self, payload):
        data = b64decode(payload['data'])
        name = payload['filename']
        image = createContentInContainer(
            self.context, u"Image", id=name, title=name, image=data
        )
        path = image.getPhysicalPath()
        portal_path = api.portal.get().getPhysicalPath()

        return '/'.join(path[len(portal_path) - 1:])

    def transform(self, block_value, event=None):
        if block_value.get('payload'):
            path = self.upload_image(block_value['payload'])

            del block_value['payload']
            block_value['url'] = path

        return block_value
