from . import PortletSerializer
from plone.app.portlets.portlets.classic import Renderer


class ClassicPortletSerializer(PortletSerializer):
    """ Portlet serializer for navigation portlet
    """

    def __call__(self):
        res = super(ClassicPortletSerializer, self).__call__()
        renderer = Renderer(
            self.context,
            self.request,
            None,
            None,
            self.assignment
        )

        res['classicportlet'] = renderer.render()

        return res
