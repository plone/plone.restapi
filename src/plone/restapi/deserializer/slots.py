# -*- coding: utf-8 -*-

""" Slots deserializers """

from plone.restapi.deserializer import json_body
from plone.restapi.events import BlocksRemovedEvent
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.slots import Slot
from plone.restapi.slots.interfaces import ISlot
from plone.restapi.slots.interfaces import ISlotStorage
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

        blocks = copy.deepcopy(data['blocks'])

        existing_blocks = self.slot.blocks

        removed_blocks_ids = set(existing_blocks.keys()) - set(blocks.keys())
        removed_blocks = {block_id: existing_blocks[block_id] for block_id in
                          removed_blocks_ids}

        notify(BlocksRemovedEvent(dict(context=self.context, blocks=removed_blocks)))

        # we don't want to store blocks that are inherited
        for k, v in blocks.items():
            if v.get('_v_inherit'):
                del blocks[k]

        for id, block_value in blocks.items():
            block_type = block_value.get("@type", "")

            handlers = []
            for h in subscribers(
                (self.slot, self.request),
                IBlockFieldDeserializationTransformer,
            ):
                if h.block_type == block_type or h.block_type is None:
                    handlers.append(h)

            for handler in sorted(handlers, key=lambda h: h.order):
                if not getattr(handler, "disabled", False):
                    block_value = handler(block_value)

            blocks[id] = block_value

        self.slot.blocks = blocks
        self.slot.blocks_layout = data['blocks_layout']
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
                    blocks=slot.blocks
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
