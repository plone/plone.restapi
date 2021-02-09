# -*- coding: utf-8 -*-

from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISlots
from plone.restapi.interfaces import ISlotStorage
from plone.restapi.serializer.converters import json_compatible
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
        self.engine = ISlots(self.context)
        self.slot_names = self.engine.discover_slots()
        self.editable_slots = self.engine.get_editable_slots()

        if self.params and len(self.params) > 0:
            return self.replySlot()

        storage = ISlotStorage(self.context)

        adapter = getMultiAdapter(
            (self.context, storage, self.request), ISerializeToJson
        )
        result = adapter()

        result['edit_slots'] = json_compatible(self.editable_slots)

        # update "edit:True" editable status in slots
        # for k, v in result['items'].items():
        #     result['items'][k]['edit'] = k in self.editable_slots

        return result

    def replySlot(self):
        name = self.params[0]

        if name not in self.slot_names:
            self.request.response.setStatus(404)
            return {
                "type": "NotFound",
                "message": 'Slot "{}" could not be found.'.format(self.params[0]),
            }

        marker = object()
        storage = ISlotStorage(self.context)
        slot = storage.get(name, marker)
        if slot is marker:      # if slot is not on this level, we create a fake one
            slot = Slot()       # TODO: replace with a DummyProxySlot
            slot.__parent__ = self.storage
            slot.__name__ = name

        result = getMultiAdapter(
            (self.context, slot, self.request), ISerializeToJson
        )()

        result['edit'] = name in self.editable_slots

        # TODO: add transaction doom, to deal with annotations created by ISlotStorage ?
        return result
