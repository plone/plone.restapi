# -*- coding: utf-8 -*-

from AccessControl.SecurityManagement import getSecurityManager
from copy import deepcopy
from persistent import Persistent
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISlot
from plone.restapi.interfaces import ISlots
from plone.restapi.interfaces import ISlotStorage
from plone.restapi.permissions import ModifySlotsPermission
from plone.restapi.slots.interfaces import ISlotSettings
from Products.CMFCore.interfaces import IContentish
from zope.annotation.factory import factory
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryAdapter
from zope.container.btree import BTreeContainer
from zope.container.contained import Contained
from zope.interface import implementer
from zope.traversing.interfaces import ITraversable


SLOTS_KEY = "plone.restapi.slots"
DEFAULT_SLOT_DATA = {
    "slot_blocks_layout": {"items": []},
    "slot_blocks": {}
}


@adapter(IContentish)
@implementer(ISlotStorage)
class PersistentSlots(BTreeContainer):
    """ Slots container"""


SlotsStorage = factory(PersistentSlots, SLOTS_KEY)


@implementer(ISlot)
class Slot(Contained, Persistent):
    """A container for data pertaining to a single slot"""

    def __init__(self, **data):
        super(Slot, self).__init__()

        for k, v in deepcopy(DEFAULT_SLOT_DATA).items():
            setattr(self, k, v)

        for k, v in data.items():
            setattr(self, k, v)


@implementer(ISlots)
@adapter(ITraversable)
class Slots(object):
    """ The slots engine provides slots functionality for a content item
    """

    def __init__(self, context):
        self.context = context

    def discover_slots(self):
        current = self.context
        names = set()
        while True:
            storage = queryAdapter(current, ISlotStorage)
            if storage is None:
                break
            for k in storage.keys():
                names.add(k)
            if current.__parent__:
                current = current.__parent__
            else:
                break

        return names

    def get_fills_stack(self, name):
        slot_stack = []

        current = self.context
        while True:
            storage = queryAdapter(current, ISlotStorage)
            if storage is None:
                break
            slot = storage.get(name)
            if slot:
                slot_stack.append(slot)
            else:
                slot_stack.append(None)
            if current.__parent__:
                current = current.__parent__
            else:
                break

        return slot_stack

    def get_blocks(self, name):
        blocks = {}
        blocks_layout = []

        _replaced = set()
        _blockmap = {}

        stack = self.get_fills_stack(name)

        level = 0
        for slot in stack:
            if slot is None:
                level += 1
                continue

            for uid, block in slot.slot_blocks.items():
                block = deepcopy(block)
                _blockmap[uid] = block

                if not (uid in blocks or uid in _replaced):
                    other = block.get('s:isVariantOf') or block.get('s:sameAs')
                    if other:
                        _replaced.add(other)

                    blocks[uid] = block
                    if level > 0:
                        block['_v_inherit'] = True

            for uid in slot.slot_blocks_layout['items']:
                if not (uid in blocks_layout or uid in _replaced):
                    blocks_layout.append(uid)

            level += 1

        for k, v in blocks.items():
            if v.get('s:sameAs'):
                v['_v_inherit'] = True
                v.update(self._resolve_block(v, _blockmap))

        return {
            'slot_blocks': blocks,
            'slot_blocks_layout': {'items': blocks_layout}
        }

    def _resolve_block(self, block, blocks):
        sameAs = block.get('s:sameAs')

        if sameAs:
            return self._resolve_block(blocks[sameAs], blocks)

        return block

    def save_data_to_slot(self, slot, data):
        to_save = {}

        for key in data['slot_blocks_layout']['items']:
            block = data['slot_blocks'][key]
            if not (block.get('s:sameOf') or block.get('_v_inherit')):
                to_save[key] = block

        slot.slot_blocks_layout = data['slot_blocks_layout']
        slot.slot_blocks = to_save
        slot._p_changed = True

    def get_editable_slots(self):
        sm = getSecurityManager()

        slot_names = self.discover_slots()

        if sm.checkPermission(ModifySlotsPermission, self.context):
            return list(slot_names)

        if not sm.checkPermission("Modify portal content", self.context):
            return []

        registry = getUtility(IRegistry)
        records = registry.forInterface(ISlotSettings)

        content_slots = [s for s in
                         [line.strip() for line in (records.content_slots or [])]
                         if s in slot_names]
        return content_slots
