# -*- coding: utf-8 -*-

from plone.restapi.behaviors import IBlocks
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import List
from zope.schema import TextLine


class ISlots(Interface):
    """Slots are named container of sets of blocks"""


class ISlotStorage(Interface):
    """ A store of slots information """


class ISlot(IBlocks):
    """Slots follow the IBlocks model"""

    block_parent = Bool(title=u"Block inheritance of slot fills")


class ISlotSettings(Interface):
    content_slots = List(
        title=u"Content slots",
        description=u'Editable slots using "Modify portal content" permission',
        value_type=TextLine(title=u"Slot name"),
    )
