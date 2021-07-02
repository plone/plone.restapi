# -*- coding: utf-8 -*-

""" Slots deserializers """

from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.slots import Slot
from plone.restapi.slots.interfaces import ISlot
from plone.restapi.slots.interfaces import ISlots
from plone.restapi.slots.interfaces import ISlotStorage
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import subscribers
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import copy


# from plone.restapi.events import BlocksRemovedEvent
# from zope.event import notify


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

        if not data:
            return

        incoming_blocks = copy.deepcopy(data["blocks"])

        engine = ISlots(self.context)
        all_blocks_ids = engine.get_blocks(self.slot.__name__, full=True)["blocks"].keys()
        parent_block_ids = list(set(all_blocks_ids) - set(self.slot.blocks.keys()))

        # don't keep blocks that are not in incoming data
        for k in list(self.slot.blocks.keys()):
            if not ((k in parent_block_ids) or (k in incoming_blocks.keys())):
                del self.slot.blocks[k]

        inherited = []
        # don't store blocks that are inherited, keep only those that really exist
        for k, v in list(incoming_blocks.items()):
            if v.get("_v_inherit"):
                del incoming_blocks[k]
                if k in parent_block_ids:
                    inherited.append(k)

        slot = self.slot.__of__(self.context)

        for id, block_value in incoming_blocks.items():
            block_type = block_value.get("@type", "")

            handlers = []
            for h in subscribers(
                (slot, self.request),
                IBlockFieldDeserializationTransformer,
            ):
                if h.block_type == block_type or h.block_type is None:
                    handlers.append(h)

            for handler in sorted(handlers, key=lambda h: h.order):
                if not getattr(handler, "disabled", False):
                    block_value = handler(block_value)

            incoming_blocks[id] = block_value

        self.slot.blocks = incoming_blocks

        # don't keep block ids in layout if they're nowhere in the inheritance tree
        all_ids = parent_block_ids + list(self.slot.blocks.keys()) + inherited
        layout = [b for b in data["blocks_layout"]["items"] if b in all_ids]
        data["blocks_layout"]["items"] = layout
        self.slot.blocks_layout = data["blocks_layout"]

        self.slot.block_parent = data.get('block_parent', False)
        self.slot._p_changed = True


@adapter(IPloneSiteRoot, ISlot, IBrowserRequest)
@implementer(IDeserializeFromJson)
class SlotDeserializerRoot(SlotDeserializer):
    """ Deserializer of one slot for site root """


@adapter(IContentish, ISlotStorage, IBrowserRequest)
@implementer(IDeserializeFromJson)
class SlotsDeserializer(object):
    """Default deserializer of slots"""

    def __init__(self, context, storage, request):
        self.context = context
        self.storage = storage
        self.request = request

    def __call__(self, data=None):
        if data is None:
            data = json_body(self.request)

        for name, slot in self.storage.items():
            incoming_data = data.get(name, None)

            # remove the existing slot data if the slot doesn't exist in new data
            if not incoming_data:
                # notify(BlocksRemovedEvent(dict(
                #     context=self.context,
                #     blocks=slot.blocks
                # )))

                self.storage[name].blocks = {}
                self.storage[name].blocks_layout = {"items": []}

        for name, incoming_data in data.items():
            if name not in self.storage:
                # create new slots when found in incoming data
                self.storage[name] = Slot()

            deserializer = getMultiAdapter(
                (self.context, self.storage[name], self.request), IDeserializeFromJson
            )
            deserializer(incoming_data)


@adapter(IPloneSiteRoot, ISlotStorage, IBrowserRequest)
@implementer(IDeserializeFromJson)
class SlotsDeserializerRoot(SlotsDeserializer):
    """ Deserializer of slots for site root """
