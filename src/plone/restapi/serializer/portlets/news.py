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
            itemList = getMultiAdapter(
                            (brain, self.request), ISerializeToJsonSummary)()
            ploneview = getMultiAdapter(
                            (self.context, self.request), name='plone')
            itemList['date'] = ploneview.toLocalizedTime(brain.created)
            itemList['thumb'] = ''
            if self.thumb_scale and brain.getIcon:
                itemList['thumb'] = '{}/@@images/image/{}'.format(
                                    brain.getURL(), self.thumb_scale())
            items.append(itemList)
        res = {'items': items}
        return res
