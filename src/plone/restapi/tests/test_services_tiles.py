# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.tiles.type import TileType
from zope.component import provideAdapter, provideUtility
from zope.interface import Interface
from plone.tiles.interfaces import IBasicTile
from plone.tiles import Tile

import transaction
import unittest


class SampleTile(Tile):

    __name__ = 'sample.tile'  # would normally be set by a ZCML handler

    def __call__(self):
        return '<html><body><b>My tile</b></body></html>'


class TestServicesTiles(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.doc = createContentInContainer(
            self.portal, u'Document',
            id=u'doc',
            title=u'A document')
        transaction.commit()

        sampleTileType = TileType(
            u'sample.tile',
            u'Sample tile',
            'cmf.ModifyPortalContent',
            'zope.Public',
            description=u'A tile used for testing',
            schema=None,
            icon='testicon')
        provideUtility(sampleTileType, name=u'sample.tile')
        provideAdapter(SampleTile, (Interface, Interface),
                       IBasicTile, name=u'sample.tile')

    def test_get_available_tiles(self):
        response = self.api_session.get('/@tiles')

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEquals(len(response), 1)
        self.assertEquals(
            response[0]['@id'],
            u'http://localhost:55001/plone/@tiles/sample.tile')
        self.assertEquals(response[0]['title'], u'Sample tile')
        self.assertEquals(
            response[0]['description'], u'A tile used for testing')
        self.assertEquals(response[0]['icon'], 'testicon')
