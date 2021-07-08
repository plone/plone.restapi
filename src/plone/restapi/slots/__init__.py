# -*- coding: utf-8 -*-

from .interfaces import ISlot
from .interfaces import ISlots
from .interfaces import ISlotStorage
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import Implicit
from copy import deepcopy
from persistent import Persistent
from plone.registry.interfaces import IRegistry
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
DEFAULT_SLOT_DATA = {"blocks_layout": {"items": []}, "blocks": {}}


@adapter(IContentish)
@implementer(ISlotStorage)
class PersistentSlots(BTreeContainer):
    """ Slots container"""


SlotsStorage = factory(PersistentSlots, SLOTS_KEY)


@implementer(ISlot)
class Slot(Persistent, Contained, Implicit):
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
    """The slots engine provides slots functionality for a content item"""

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

    def get_data(self, name, full=False):
        blocks = {}
        blocks_layout = []
        hidden = []

        _replaced = set()
        _seen_blocks = {}

        stack = self.get_fills_stack(name)

        level = 0
        for slot in stack:
            if slot is None:
                level += 1
                continue

            for uid, block in slot.blocks.items():
                block = deepcopy(block)
                _seen_blocks[uid] = block

                if not (uid in blocks or uid in _replaced):
                    other = block.get("s:isVariantOf") or block.get("s:sameAs")
                    if other:
                        _replaced.add(other)

                    if (not full) and block.get('v:hidden'):
                        hidden.append(uid)
                        continue

                    blocks[uid] = block

                    if level > 0:   # anything deeper than "top" level is inherited
                        block["_v_inherit"] = True
                        block["readOnly"] = True

            for uid in slot.blocks_layout["items"]:
                if not (uid in blocks_layout or uid in _replaced):
                    blocks_layout.append(uid)

            level += 1

            if getattr(slot, 'block_parent', False) and not full:
                break

        for k, v in blocks.items():
            if v.get("s:sameAs"):
                v.update(self._resolve_block(v, _seen_blocks))
                v["_v_inherit"] = True
                v["readOnly"] = True        # TODO: should we set this here?
                # v['_v_original'] = self._resolve_block(v, _seen_blocks)

        for k, v in blocks.items():
            if v.get("s:isVariantOf"):
                # in the frontend, if we have a block that's hidden then we go and
                # "unhide", we'll need the original data for best UX
                v['_v_original'] = deepcopy(_seen_blocks[v.get("s:isVariantOf")])

        return {
            "blocks": blocks,
            "blocks_layout": {
                "items": [b for b in blocks_layout if b in _seen_blocks.keys()
                          and b not in hidden]
            },
        }

    def _resolve_block(self, block, blocks):
        sameAs = block.get("s:sameAs")

        if sameAs:
            return self._resolve_block(blocks[sameAs], blocks)

        return block

    def save_data_to_slot(self, slot, data):
        to_save = {}

        for key in data["blocks_layout"]["items"]:
            block = data["blocks"][key]
            if not (block.get("s:sameOf") or block.get("_v_inherit")):
                to_save[key] = block

        slot.blocks_layout = data["blocks_layout"]
        slot.blocks = to_save
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

        content_slots = [
            s
            for s in [line.strip() for line in (records.content_slots or [])]
            if s in slot_names
        ]
        return content_slots
