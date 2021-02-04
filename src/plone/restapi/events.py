from plone.restapi.interfaces import ISlotRemovedEvent
from zope.event import Event
from zope.interface import implements


class SlotRemovedEvent(Event):
    implements(ISlotRemovedEvent)

    def __init__(self, info):
        self.info = info
