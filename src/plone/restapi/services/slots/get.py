# -*- coding: utf-8 -*-

from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISlots
from plone.restapi.interfaces import ISlotStorage
from plone.restapi.services import Service
from plone.restapi.slots import Slot
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class SlotsGet(Service):
    """Returns the available slots."""

    def __init__(self, context, request):
        super(SlotsGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        if self.params and len(self.params) > 0:
            return self.replySlot()

        storage = ISlotStorage(self.context)

        adapter = getMultiAdapter(
            (self.context, storage, self.request), ISerializeToJson
        )

        return adapter()

    def replySlot(self):
        name = self.params[0]

        engine = ISlots(self.context)
        slot_names = engine.discover_slots()

        if name not in slot_names:
            self.request.response.setStatus(404)
            return {
                "type": "NotFound",
                "message": 'Slot "{}" could not be found.'.format(self.params[0]),
            }

        marker = object()
        storage = ISlotStorage(self.context)
        slot = storage.get(name, marker)
        if slot is marker:      # if slot is not on this level, we create a fake one
            slot = Slot()
            slot.__parent__ = self.storage
            slot.__name__ = name

        adapter = getMultiAdapter(
            (self.context, slot, self.request), ISerializeToJson
        )
        return adapter()
