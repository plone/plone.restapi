# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.schema import List
from zope.schema import TextLine


class ISlotSettings(Interface):
    content_slots = List(
        title=u"Content slots",
        description=u'Editable slots using "Modify portal content" permission',
        value_type=TextLine(title=u"Slot name")
    )
