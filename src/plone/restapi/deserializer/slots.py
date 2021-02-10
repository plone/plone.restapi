# -*- coding: utf-8 -*-

""" Slots deserializers """

from plone.restapi.deserializer import json_body
from plone.restapi.events import BlocksRemovedEvent
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISlot
from plone.restapi.interfaces import ISlotStorage
from plone.restapi.slots import Slot
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import subscribers
from zope.event import notify
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import copy


@adapter(IContentish, ISlot, IBrowserRequest)
@implementer(IDeserializeFromJson)
class SlotDeserializer(object):
    """ Deserializer of one slot for contentish objects """

    def __init__(self, context, slot, request):
        self.context = context
        self.slot = slot
        self.request = request

    def __call__(self, data=None):
        if data is None:
            data = json_body(self.request)

        slot_blocks = copy.deepcopy(data['slot_blocks'])

        existing_blocks = self.slot.slot_blocks

        removed_blocks_ids = set(existing_blocks.keys()) - set(slot_blocks.keys())
        removed_blocks = {block_id: existing_blocks[block_id] for block_id in
                          removed_blocks_ids}

        notify(BlocksRemovedEvent(dict(context=self.context, blocks=removed_blocks)))

        for id, block_value in slot_blocks.items():
            block_type = block_value.get("@type", "")

            handlers = []
            for h in subscribers(
                (self.context, self.request),
                IBlockFieldDeserializationTransformer,
            ):
                if h.block_type == block_type or h.block_type is None:
                    handlers.append(h)

            for handler in sorted(handlers, key=lambda h: h.order):
                if not getattr(handler, "disabled", False):
                    block_value = handler(block_value)

            slot_blocks[id] = block_value

        self.slot.slot_blocks = slot_blocks
        self.slot.slot_blocks_layout = data['slot_blocks_layout']
        self.slot._p_changed = True


@adapter(IPloneSiteRoot, ISlot, IBrowserRequest)
@implementer(IDeserializeFromJson)
class SlotDeserializerRoot(SlotDeserializer):
    """ Deserializer of one slot for site root """


@adapter(IContentish, ISlotStorage, IBrowserRequest)
@implementer(IDeserializeFromJson)
class SlotsDeserializer(object):
    """ Default deserializer of slots
    """

    def __init__(self, context, storage, request):
        self.context = context
        self.storage = storage
        self.request = request

    def __call__(self, data=None):
        if data is None:
            data = json_body(self.request)

        for name, slot in self.storage.items():
            slotdata = data.get(name, None)
            if slotdata is None:
                notify(BlocksRemovedEvent(dict(
                    context=self.context,
                    blocks=slot.slot_blocks
                )))

                del self.storage[name]

        for name, slotdata in data.items():
            if name not in self.storage:
                slot = Slot()
                self.storage[name] = slot
            else:
                slot = self.storage[name]

            deserializer = getMultiAdapter(
                (self.context, slot, self.request), IDeserializeFromJson
            )
            deserializer(slotdata)


@adapter(IPloneSiteRoot, ISlotStorage, IBrowserRequest)
@implementer(IDeserializeFromJson)
class SlotsDeserializerRoot(SlotsDeserializer):
    """ Deserializer of slots for site root """
