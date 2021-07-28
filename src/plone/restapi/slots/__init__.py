# -*- coding: utf-8 -*-

from .interfaces import ISlot
from .interfaces import ISlots
from .interfaces import ISlotStorage
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import Implicit
from copy import deepcopy
from OFS.Traversable import Traversable
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
    """Slots container"""


SlotsStorage = factory(PersistentSlots, SLOTS_KEY)


@implementer(ISlot)
class Slot(Persistent, Contained, Implicit, Traversable):
    """A container for data pertaining to a single slot"""

    def __init__(self, **data):
        super(Slot, self).__init__()

        for k, v in deepcopy(DEFAULT_SLOT_DATA).items():
            setattr(self, k, v)

        for k, v in data.items():
            setattr(self, k, v)

    def getPhysicalPath(self):
        """ Return physical path

        Override, to be able to provide a fake name for the physical path
        """
        path = super(Slot, self).getPhysicalPath()[:-1]     # last bit is RestWrapper

        res = tuple([''] + [bit for bit in path[1:] if bit])
        path = () + res[:-1] + ('++slots++' + path[-1],)

        print('path', path)
        return path


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

    def keys(self):
        return self.discover_slots()

    def __contains__(self, name):
        return name in self.keys()

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
        _blocks = {}  # the resulting blocks
        _blocks_layout = []  # a tentative block_layout ordered list
        _hidden = []  # list of block uids that are hidden
        _seen_blocks = {}  # all blocks in this hierarchy
        _replaced = set()  # original blocks that are overridden by variants. We
        _inherited = set()  # block uids that are inherited
        # don't want to include these in the final output

        __to_include_originals = []  # these blocks need to reference their original

        stack = self.get_fills_stack(name)

        # TODO: I think the block data gets overridden when it's an inherited block

        for level, slot in enumerate(stack):
            if slot is None:
                continue

            for uid, block in slot.blocks.items():
                block = deepcopy(block)
                _seen_blocks[uid] = block

                if not (uid in _blocks):  # or uid in _replaced
                    other = block.get("s:isVariantOf") or block.get("s:sameAs")
                    if other:
                        _replaced.add(other)
                        __to_include_originals.append(block)

                    if block.get("v:hidden") and (not full):
                        _hidden.append(uid)  # we exclude hidden blocks
                        continue

                    if level > 0:  # anything deeper than "top" level is inherited
                        _inherited.add(uid)

                    if uid not in _replaced:
                        _blocks[uid] = block

            for uid in slot.blocks_layout["items"]:
                if not (uid in _blocks_layout or uid in _replaced):
                    # inherited blocks are placed at the end
                    _blocks_layout.append(uid)

            if getattr(slot, "block_parent", False) and not full:
                break

        for k, v in _blocks.items():

            if k in _inherited:
                v["_v_inherit"] = True
                v["readOnly"] = True

            if v.get("s:sameAs"):
                v.update(self._resolve_block(v, _seen_blocks))
                v["_v_inherit"] = True
                v["readOnly"] = True  # TODO: should we set this here?
                # v['_v_original'] = self._resolve_block(v, _seen_blocks)

        # in the frontend, if we have a block that's hidden then we go and
        # "unhide", we'll need the original data for best UX

        for v in __to_include_originals:
            # original = deepcopy(_seen_blocks[v.get("s:isVariantOf")])
            original = _seen_blocks.get(v.get("s:isVariantOf"), None)

            # TODO: what do do when the inherited block has been deleted?
            if original is not None:
                v["_v_original"] = original

        return {
            "blocks": _blocks,
            "blocks_layout": {
                "items": [
                    b
                    for b in _blocks_layout
                    if b in _seen_blocks.keys() and b not in _hidden
                ]
            },
        }

    def _resolve_block(self, block, blocks):
        sameAsUID = block.get("s:sameAs")

        if sameAsUID:
            if sameAsUID in blocks:
                return self._resolve_block(blocks[sameAsUID], blocks)
            else:
                return None

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
