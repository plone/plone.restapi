# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.tiles import Tile
from plone.tiles.interfaces import IBasicTile
from plone.tiles.type import TileType
from zope.component import provideAdapter
from zope.component import provideUtility
from zope.component import queryUtility
from zope.interface import Interface

import transaction
import unittest
import zope.schema


class ISampleTile(Interface):
    title = zope.schema.TextLine(
        title=u'Title',
        required=False
    )


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

        fti = queryUtility(
            IDexterityFTI,
            name='Document')
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append('plone.tiles')
        behavior_list.append('plone.leadimage')
        fti.behaviors = tuple(behavior_list)

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
            schema=ISampleTile,
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
            self.portal_url + u'/@tiles/sample.tile')
        self.assertEquals(response[0]['title'], u'Sample tile')
        self.assertEquals(
            response[0]['description'], u'A tile used for testing')
        self.assertEquals(response[0]['icon'], 'testicon')

    def test_get_tile(self):
        response = self.api_session.get('/@tiles/sample.tile')

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEquals(response['title'], u'Sample tile')
        self.assertEquals(
            response['properties']['title']['title'], u'Title')
        self.assertEquals(
            response['properties']['title']['type'], u'string')

    def test_patch_tiles_list(self):
        response = self.api_session.patch(
            '/doc',
            json={
                "tiles": {
                    'uuid1': {'@type': 'title'},
                    'uuid2': {'@type': 'description'}
                },
            })

        self.assertEqual(response.status_code, 204)

        response = self.api_session.get('/doc')
        response = response.json()

        self.assertEquals(
            response['tiles'],
            {
                'uuid1': {'@type': 'title'},
                'uuid2': {'@type': 'description'}
            }
        )

    def test_patch_tiles_layout(self):
        response = self.api_session.patch(
            '/doc',
            json={
                "tiles_layout": {
                    "items": ["#uuid1", "#uuid2"]
                }
            })

        self.assertEqual(response.status_code, 204)

        response = self.api_session.get('/doc')
        response = response.json()

        self.assertEquals(
            response['tiles_layout'],
            {
                "items": ["#uuid1", "#uuid2"]
            }
        )

    def test_get_tiles_layout_schema(self):
        response = self.api_session.get('/@types/Document')

        self.assertEqual(response.status_code, 200)
        response = response.json()

    # These are not failing because the patch operations doesn't validate
    # fields right now
    # def test_patch_tiles_list_wrong_type(self):
    #     response = self.api_session.patch(
    #         '/doc',
    #         json={
    #             "tiles": [{'uuid1': {'@type': 'title'}}]
    #         })
    #     self.assertEqual(response.status_code, 500)

    # def test_patch_tiles_layout_wrong_type(self):
    #     response = self.api_session.patch(
    #         '/doc',
    #         json={
    #             "tiles_layout": {'uuid1': {'@type': 'title'}}
    #         })
    #     self.assertEqual(response.status_code, 500)
