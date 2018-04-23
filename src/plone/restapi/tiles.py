# -*- coding: utf-8 -*-
from uuid import uuid4
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


ATTRIBUTE_NAME = 'tiles'


class ITilesStorage(Interface):
    """ Adapt an object to this interface to manage the favorites of an
        object.
    """

    def get():
        """ Return the list of tiles """

    def add(username):
        """ Add the tile to the storage """

    def remove(self, username):
        """ Remove the tile from the storage """

    def order(self, tile, position):
        """ Reorder the tile to the given position """


@implementer(ITilesStorage)
@adapter(Interface)
class TilesStorage(object):

    def __init__(self, context):
        self.context = context
        self.tiles = self.get()
        if not self.tiles:
            setattr(self.context, ATTRIBUTE_NAME, self.tiles)

    def get(self):
        return getattr(self.context, ATTRIBUTE_NAME, [])

    def add(self, tile):
        tile.update({'uuid': str(uuid4())})
        self.tiles.append(tile)
        setattr(self.context, ATTRIBUTE_NAME, self.tiles)

    def remove(self, uuid):
        index_to_delete = [tile['uuid'] for tile in self.tiles].index(uuid)
        del self.tiles[index_to_delete]
        setattr(self.context, ATTRIBUTE_NAME, self.tiles)

    def order(self, uuid, position):
        index_to_delete = [tile['uuid'] for tile in self.tiles].index(uuid)
        tile = self.tiles[index_to_delete]
        del self.tiles[index_to_delete]
        self.tiles.insert(position, tile)
        setattr(self.context, ATTRIBUTE_NAME, self.tiles)
