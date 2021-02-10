# -*- coding: utf-8 -*-

from plone.api import portal
from plone.restapi.interfaces import ISlots


def handle_block_removed_event(event):
    # TODO: needs rewrite
    info = event.object
    catalog = portal.get_tool('portal_catalog')
    blockid = info['blockid']
    brains = catalog.searchResults(slot_block_ids=blockid)

    for brain in brains:
        obj = brain.getObject()

        slots = ISlots(obj)
        for slot in slots.values():
            if blockid in slot['blocks_layout']['items']:
                slot['blocks_layout']['items'] = [
                    bid for bid in slot['blocks_layout']['items']
                    if bid != blockid
                ]
                slot._p_changed = True

        catalog.reindexObject(obj, idxs=['slot_block_ids'])


def handle_blocks_removed_event(event):
    """ Update the slot blocks layout for objects that reference some blocks
    """

    # TODO: needs rewrite
    info = event.object
    catalog = portal.get_tool('portal_catalog')
    blockids = info['blocks'].keys()
    brains = catalog.searchResults(slot_block_ids={'query': blockids, 'operator': 'or'})
    set_block_ids = set(blockids)

    for brain in brains:
        obj = brain.getObject()

        slots = ISlots(obj)
        for slot in slots.values():
            if set_block_ids.intersection(slot['blocks_layout']['items']):
                slot['blocks_layout']['items'] = [
                    bid for bid in slot['blocks_layout']['items']
                    if bid not in blockids
                ]
                slot._p_changed = True

        catalog.reindexObject(obj, idxs=['slot_block_ids'])
