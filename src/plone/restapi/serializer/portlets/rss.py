from . import PortletSerializer
from zope.component import getMultiAdapter
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.app.portlets.portlets.rss import Renderer


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
        items = []
        self.update()
        rsss = self.items
        # import pdb; pdb.set_trace()
        for rss in rsss:
            rss['updated'] = rss['updated'].strftime('%Y-%m-%d %X %Z').strip()
            items.append(rss)
        return {'items': items}
