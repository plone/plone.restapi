# -*- coding: utf-8 -*-

from plone.indexer.decorator import indexer
from plone.restapi.slots import SLOTS_KEY
from plone.restapi.slots.interfaces import ISlotStorage
from Products.CMFCore.interfaces import IContentish
from zope.annotation.interfaces import IAnnotations


@indexer(IContentish)
def slot_block_ids(obj):
    if SLOTS_KEY not in IAnnotations(obj):
        return

    blocks = []
    storage = ISlotStorage(obj)
    for name, slot in storage.items():
        blocks.extend(slot.blocks_layout["items"])

    return blocks
