from . import PortletSerializer
from plone.app.portlets.portlets.rss import Renderer
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import getMultiAdapter


class RssPortletSerializer(PortletSerializer):
    """ Portlet serializer for news portlet
    """

    def __call__(self):
        res = super(RssPortletSerializer, self).__call__()
        renderer = RssPortletRenderer(
            self.context,
            self.request,
            None,
            None,
            self.assignment
        )
        res['rssportlet'] = renderer.render()

        return res


class RssPortletRenderer(Renderer):
    def render(self):
        self.update()
        items = []

        for o in self.items:
            o['updated'] = o['updated'].strftime('%Y-%m-%d %X %Z').strip()
            items.append(o)

        return {'items': items}
