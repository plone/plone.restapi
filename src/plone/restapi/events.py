# -*- coding: utf-8 -*-

from plone.restapi.interfaces import IBlockRemovedEvent
from plone.restapi.interfaces import IBlocksRemovedEvent
from zope.interface import implementer
from zope.interface.interfaces import ObjectEvent


@implementer(IBlockRemovedEvent)
class BlockRemovedEvent(ObjectEvent):

    def __init__(self, object):
        self.object = object


@implementer(IBlocksRemovedEvent)
class BlocksRemovedEvent(ObjectEvent):

    def __init__(self, object):
        self.object = object
