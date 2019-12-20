from . import PortletSerializer
from plone.app.portlets.portlets.login import Renderer


class LoginPortletSerializer(PortletSerializer):
    """ Portlet serializer for static portlet
    """

    def __call__(self):
        res = super(StaticTextPortletSerializer, self).__call__()
        renderer = StaticTextPortletRenderer(
            self.context,
            self.request,
            None,
            None,
            self.assignment
        )

        res['statictextportlet'] = renderer.render()

        return res


class LoginPortletRenderer(Renderer):
    def render(self):
        res = {
            'text': self.transformed(),
        }

        return res
