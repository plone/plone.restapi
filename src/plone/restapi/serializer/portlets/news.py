from . import PortletSerializer
from zope.component import getMultiAdapter
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.app.portlets.portlets.news import Renderer


class NewsPortletSerializer(PortletSerializer):
    """ Portlet serializer for news portlet
    """

    def __call__(self):
        res = super(NewsPortletSerializer, self).__call__()
        renderer = NewsPortletRenderer(
            self.context,
            self.request,
            None,
            None,
            self.assignment
        )
        res['newsportlet'] = renderer.render()

        return res


class NewsPortletRenderer(Renderer):
    def render(self):
        items = []
        brains = self.published_news_items()
        for brain in brains:
            itemList = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
            itemList['date'] = brain.created.strftime('%Y-%m-%d %X')
            items.append(itemList)
        res = {'items': items}
        return res
