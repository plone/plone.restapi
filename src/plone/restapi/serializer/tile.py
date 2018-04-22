# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.interface import implementer
from zope.interface import Interface
from plone.tiles.interfaces import ITileType
from zope.component import adapter
from zope.component.hooks import getSite

SERVICE_ID = '@tiles'


@implementer(ISerializeToJsonSummary)
@adapter(ITileType, Interface)
class TileSummarySerializeToJson(object):

    def __init__(self, tile, request):
        self.tile = tile

    def __call__(self):
        portal = getSite()
        return {
            '@id': '{}/{}/{}'.format(
                portal.absolute_url(),
                SERVICE_ID,
                self.tile.__name__
            ),
            'title': self.tile.title,
            'description': self.tile.description,
            'icon': self.tile.icon,
        }
