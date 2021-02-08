# -*- coding: utf-8 -*-

from plone.api import portal
from plone.restapi.interfaces import IBlockRemovedEvent
from plone.restapi.interfaces import IBlocksRemovedEvent
from plone.restapi.interfaces import ISlots
from zope.interface import implements
from zope.interface.interfaces import ObjectEvent


class BlockRemovedEvent(ObjectEvent):
    implements(IBlockRemovedEvent)

    def __init__(self, object):
        self.object = object


class BlocksRemovedEvent(ObjectEvent):
    implements(IBlocksRemovedEvent)

    def __init__(self, object):
        self.object = object


def handle_block_removed_event(event):
    info = event.object
    catalog = portal.get_tool('portal_catalog')
    blockid = info['blockid']
    brains = catalog.searchResults(slot_block_ids=blockid)

    for brain in brains:
        obj = brain.getObject()

        slots = ISlots(obj)
        for slot in slots.values():
            if blockid in slot['slot_blocks_layout']['items']:
                slot['slot_blocks_layout']['items'] = [
                    bid for bid in slot['slot_blocks_layout']['items']
                    if bid != blockid
                ]
                slot._p_changed = True

        catalog.reindexObject(obj, idxs=['slot_block_ids'])


def handle_blocks_removed_event(event):
    """ Update the slot blocks layout for objects that reference some blocks
    """

    info = event.object
    catalog = portal.get_tool('portal_catalog')
    blockids = info['blocks'].keys()
    brains = catalog.searchResults(slot_block_ids={'query': blockids, 'operator': 'or'})
    set_block_ids = set(blockids)

    for brain in brains:
        obj = brain.getObject()

        slots = ISlots(obj)
        for slot in slots.values():
            if set_block_ids.intersection(slot['slot_blocks_layout']['items']):
                slot['slot_blocks_layout']['items'] = [
                    bid for bid in slot['slot_blocks_layout']['items']
                    if bid not in blockids
                ]
                slot._p_changed = True

        catalog.reindexObject(obj, idxs=['slot_block_ids'])
