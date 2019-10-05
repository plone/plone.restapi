# -*- coding: utf-8 -*-
from AccessControl.security import checkPermission
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from plone.tiles.interfaces import ITileType
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class TilesGet(Service):
    def __init__(self, context, request):
        super(TilesGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        if self.params and len(self.params) > 0:
            self.content_type = "application/json+schema"
            try:
                block = getUtility(ITileType, name=self.params[0])
                return getMultiAdapter((block, self.request), ISerializeToJson)()
            except KeyError:
                self.content_type = "application/json"
                self.request.response.setStatus(404)
                return {
                    "type": "NotFound",
                    "message": 'Tile "{}" could not be found.'.format(self.params[0]),
                }

        result = []
        blocks = getUtilitiesFor(ITileType, context=self.context)
        for name, block in blocks:
            serializer = getMultiAdapter((block, self.request), ISerializeToJsonSummary)
            if checkPermission(block.add_permission, self.context):
                result.append(serializer())

        return result
