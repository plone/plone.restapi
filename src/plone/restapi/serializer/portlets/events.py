from . import PortletSerializer
from zope.component import getMultiAdapter
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.app.event.portlets.portlet_events import Renderer


class EventsPortletSerializer(PortletSerializer):
    """ Portlet serializer for events portlet
    """

    def __call__(self):
        res = super(EventsPortletSerializer, self).__call__()
        renderer = EventsPortletRenderer(
            self.context,
            self.request,
            None,
            None,
            self.assignment
        )
        res['eventsportlet'] = renderer.render()

        return res


class EventsPortletRenderer(Renderer):
    def render(self):
        items = []
        for event in self.events:
            itemList = getMultiAdapter(
                (event.context, self.request),
                ISerializeToJsonSummary)()
            itemList['location'] = event.context.location
            itemList['url'] = event.context.event_url
            itemList['formatted_date'] = event.start.strftime('%Y-%m-%dT%H:%M:%S%z')
            items.append(itemList)
        self.update()
        res = {
            'items': items,
            'prev_url': self.prev_url,
            'next_url': self.next_url
        }
        return res
