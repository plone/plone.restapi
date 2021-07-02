# -*- coding: utf-8 -*-

from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.slots import Slot
from plone.restapi.slots.interfaces import ISlot
from plone.restapi.slots.interfaces import ISlots
from plone.restapi.slots.interfaces import ISlotStorage
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import subscribers
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema import getFields

import copy


SERVICE_ID = "@slots"

_MISSING = object()


def serialize_data(slot, request, schema):
    result = {}
    for name, field in getFields(schema).items():
        if name in ['blocks', 'blocks_layout']:
            continue
        value = getattr(slot, name, _MISSING)
        if value is not _MISSING:
            result[json_compatible(name)] = value       # assumes JSON-compatible values

    return result


@adapter(Interface, ISlot, IBrowserRequest)
@implementer(ISerializeToJson)
class SlotSerializer(object):
    """Default serializer for a single persistent slot"""

    def __init__(self, context, slot, request):
        self.context = context
        self.request = request
        self.slot = slot

    def __call__(self, full=False):
        name = self.slot.__name__

        # a dict with blocks and blocks_layout
        data = ISlots(self.context).get_data(name, full)

        blocks = copy.deepcopy(data["blocks"])

        slot = self.slot.__of__(self.context)

        for id, block_value in blocks.items():
            block_type = block_value.get("@type", "")
            handlers = []
            for h in subscribers(
                (slot, self.request), IBlockFieldSerializationTransformer
            ):
                if h.block_type == block_type or h.block_type is None:
                    handlers.append(h)

            for handler in sorted(handlers, key=lambda h: h.order):
                if not getattr(handler, "disabled", False):
                    block_value = handler(block_value)

            blocks[id] = json_compatible(block_value)

        result = {
            "@id": "{0}/{1}/{2}".format(self.context.absolute_url(), SERVICE_ID, name),
            "blocks": blocks,
            "blocks_layout": data["blocks_layout"],
        }

        result.update(**serialize_data(slot, self.request, schema=ISlot))

        return result


@ adapter(Interface, ISlotStorage, IBrowserRequest)
@ implementer(ISerializeToJson)
class SlotsSerializer(object):
    """Default slots storage serializer"""

    def __init__(self, context, storage, request):
        self.context = context
        self.request = request
        self.storage = storage

    def __call__(self, full=False):
        base_url = self.context.absolute_url()
        result = {"@id": "{}/{}".format(base_url, SERVICE_ID), "items": {}}

        engine = ISlots(self.context)
        slot_names = engine.discover_slots()

        marker = object()
        for name in slot_names:
            slot = self.storage.get(name, marker)

            if slot is marker:  # if slot is not on this level, we create a fake one
                # TODO: deal with this better, no need for transaction.doom()
                slot = Slot()
                slot.__parent__ = self.storage
                slot.__name__ = name

            serializer = getMultiAdapter(
                (self.context, slot, self.request), ISerializeToJson
            )
            result["items"][name] = serializer(full)

        return result
