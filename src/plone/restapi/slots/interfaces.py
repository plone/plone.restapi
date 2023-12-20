# -*- coding: utf-8 -*-

from plone.restapi.behaviors import IBlocks
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import List
from zope.schema import TextLine


class ISlots(Interface):
    """Slots are named container of sets of blocks"""

    def discover_slots():
        """Returns a list of all persistent slot names, across the hierarchy"""

    def get_data(name):
        """Get the blocks + blocks_layout for a slot name"""

    def get_editable_slots():
        """Returns a list of slot names that can be modified by the current principal"""

    def save_data_to_slot(slot, data):
        """Persist the data for a slot"""

    def get_fills_stack():
        """Returns a list of all discovered persistent slots across a hierarchy"""


class ISlotStorage(Interface):
    """A store of slots information"""


class ISlot(IBlocks):
    """Slots follow the IBlocks model"""

    block_parent = Bool(title=u"Block inheritance of slot fills")


class ISlotSettings(Interface):
    content_slots = List(
        title=u"Content slots",
        description=u'Editable slots using "Modify portal content" permission',
        value_type=TextLine(title=u"Slot name"),
    )


"""
# special slot fill attributes:


- `s: sameAs`: Ideally blocks uids should be unique across the whole CMS. That's why we
  use uuid, right? So, when customizing the order of an inherited slot, a "placeholder"
  should be created in the current level. This placeholder would have `s: sameAs` point to
  the "overriden" parent.
- `s: isVariantOf`: An inherited block could be "copied" to another level and mutated
  there. `s: isVariantOf` points to the original source block.
- `v: hidden`: An inherited block is hidden at this level. To be used with `s: sameAs` to
  point to the "parent" block. When publishing slots ( in the `@ slots` endpoint) the
  hidden blocks are included only when run with `full = true`.
"""
