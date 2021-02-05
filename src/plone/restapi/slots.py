# -*- coding: utf-8 -*-
from .interfaces import ISlot
from .interfaces import ISlots
from persistent import Persistent
from Products.CMFCore.interfaces import IContentish
from zope.annotation.factory import factory
from zope.component import adapter
from zope.container.btree import BTreeContainer
from zope.container.contained import Contained
from zope.interface import implementer


SLOTS_KEY = "plone.restapi.slots"


@adapter(IContentish)
@implementer(ISlots)
class PersistentSlots(BTreeContainer):
    """Slots store"""


Slots = factory(PersistentSlots, SLOTS_KEY)


@implementer(ISlot)
class Slot(Contained, Persistent):
    """A container for data pertaining to a single slot"""

    def __init__(self):
        super(Slot, self).__init__()
        self.slot_blocks_layout = {"items": []}
        self.slot_blocks = {}
