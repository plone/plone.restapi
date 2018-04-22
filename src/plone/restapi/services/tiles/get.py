# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from AccessControl.security import checkPermission
from zope.component import getUtilitiesFor
from zope.component import getMultiAdapter
from plone.tiles.interfaces import ITileType
from plone.restapi.interfaces import ISerializeToJsonSummary


class TilesGet(Service):

    def reply(self):

        result = []
        tiles = getUtilitiesFor(ITileType, context=self.context)
        for name, tile in tiles:
            serializer = getMultiAdapter(
                (tile, self.request), ISerializeToJsonSummary)
            if checkPermission(tile.add_permission, self.context):
                result.append(serializer())

        return result
