from . import PortletSerializer
from plone.portlet.static.static import Renderer


class StaticPortletSerializer(PortletSerializer):
    """ Portlet serializer for static portlet
    """

    def __call__(self):
        res = super(StaticPortletSerializer, self).__call__()
        renderer = StaticPortletRenderer(
            self.context,
            self.request,
            None,
            None,
            self.assignment
        )

        res['classicportlet'] = renderer.render()

        return res


class StaticPortletRenderer(Renderer):
    def render(self):
        res = {
            'header': self.data.header,
            'text': self.transformed(),
            'omit_border': self.data.omit_border,
            'footer': self.data.footer,
            'more_url': self.data.more_url
        }
        return res
