from plone.restapi.interfaces import IConvertBlockToMarkdown
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IConvertBlockToMarkdown)
@adapter(Interface, Interface)
class ImageSerializer:
    """"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block_data):
        path = block_data.get("url", "")
        download = (
            block_data.get("image_scales", {}).get("image", [])[0].get("download")
        )
        url = path + "/" + download
        alt = block_data.get("alt", "")
        if url:
            return f"![{alt}]({url})"
