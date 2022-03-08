from . import PortletSerializer
from DateTime import DateTime
from plone.app.event.portlets.portlet_events import Renderer
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from zope.component import getMultiAdapter


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

    def as_date(self, value):
        if value:
            if isinstance(value, DateTime):
                value = value.asdatetime()

            return json_compatible(value)

    def render(self):
        items = []

        for event in self.events:
            item = getMultiAdapter(
                (event.context, self.request),
                ISerializeToJsonSummary)()

            item['location'] = event.context.location
            item['url'] = event.context.event_url

            item['created'] = self.as_date(event.created)
            item['modified'] = self.as_date(event.context.modified())
            item['effective'] = self.as_date(event.context.effective())

            item['start'] = self.as_date(event.start)
            item['end'] = self.as_date(event.end)

            items.append(item)

        self.update()
        res = {
            'items': items,
            'prev_url': self.prev_url,
            'next_url': self.next_url
        }

        return res
