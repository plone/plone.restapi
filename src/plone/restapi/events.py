# -*- coding: utf-8 -*-

from plone.restapi.interfaces import IBlockRemovedEvent
from plone.restapi.interfaces import IBlocksRemovedEvent
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
