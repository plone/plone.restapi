from AccessControl.security import checkPermission
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from plone.tiles.interfaces import ITileType
from zope.deprecation import deprecated
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import zope.deprecation
import warnings
import sys


sys.modules["plone.restapi.services.tiles"] = deprecated(
    zope.deprecation,
    "``plone.restapi.services.tiles`` is deprecated and will be removed in plone.restapi 9.",
)


@implementer(IPublishTraverse)
class TilesGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        warnings.warn(
            "``plone.restapi.services.tiles`` is deprecated and will be removed in plone.restapi 9.",
            DeprecationWarning,
        )

        if self.params and len(self.params) > 0:
            self.content_type = "application/json+schema"
            try:
                tile = getUtility(ITileType, name=self.params[0])
                return getMultiAdapter((tile, self.request), ISerializeToJson)()
            except KeyError:
                self.content_type = "application/json"
                self.request.response.setStatus(404)
                return {
                    "type": "NotFound",
                    "message": f'Tile "{self.params[0]}" could not be found.',
                }

        result = []
        tiles = getUtilitiesFor(ITileType, context=self.context)
        for name, tile in tiles:
            serializer = getMultiAdapter((tile, self.request), ISerializeToJsonSummary)
            if checkPermission(tile.add_permission, self.context):
                result.append(serializer())

        return result
