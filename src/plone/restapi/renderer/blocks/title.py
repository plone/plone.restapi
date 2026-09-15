from plone.restapi.interfaces import IConvertBlockToMarkdown
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IConvertBlockToMarkdown)
@adapter(Interface, Interface)
class TitleSerializer:
    """"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return f"# {self.context.title}"
