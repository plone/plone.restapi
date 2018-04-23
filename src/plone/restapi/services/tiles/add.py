# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
# from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
# from zope.component import queryMultiAdapter
from zExceptions import BadRequest
from zope.interface import alsoProvides
from plone.restapi.tiles import ITilesStorage
from zope.component import queryUtility
from plone.tiles.interfaces import ITileType

import plone.protect.interfaces
import zope.schema


class TilesPost(Service):
    """Creates a new group.
    """

    def reply(self):
        storage = ITilesStorage(self.context)
        data = json_body(self.request)

        if '@type' not in data:
            raise BadRequest("Property '@type' is required")

        tile_type = queryUtility(ITileType, name=data['@type'])

        if tile_type is None:
            self.content_type = "application/json"
            self.request.response.setStatus(404)
            return {
                'type': 'NotFound',
                'message': 'Tile "{}" could not be found.'.format(
                    data['@type']
                )
            }

        tile_data = {}
        for field in zope.schema.getFields(tile_type.schema):
            if field in data:
                tile_data.update({field: data[field]})

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        storage.add(tile_data)
        # Not finished...
        # self.request.response.setStatus(201)
        # self.request.response.setHeader('Location', obj.absolute_url())

        # serializer = queryMultiAdapter(
        #     (obj, self.request),
        #     ISerializeToJson
        # )
