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
    title = zope.schema.TextLine(title="Title", required=False)


class SampleTile(Tile):

    __name__ = "sample.tile"  # would normally be set by a ZCML handler

    def __call__(self):
        return "<html><body><b>My tile</b></body></html>"


class TestServicesTiles(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("plone.leadimage")
        fti.behaviors = tuple(behavior_list)

        self.doc = createContentInContainer(
            self.portal, "Document", id="doc", title="A document"
        )
        transaction.commit()

        sampleTileType = TileType(
            "sample.tile",
            "Sample tile",
            "cmf.ModifyPortalContent",
            "zope.Public",
            description="A tile used for testing",
            schema=ISampleTile,
            icon="testicon",
        )
        provideUtility(sampleTileType, name="sample.tile")
        provideAdapter(
            SampleTile, (Interface, Interface), IBasicTile, name="sample.tile"
        )

    def tearDown(self):
        self.api_session.close()

    def test_get_available_tiles(self):
        response = self.api_session.get("/@tiles")

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]["@id"], self.portal_url + "/@tiles/sample.tile")
        self.assertEqual(response[0]["title"], "Sample tile")
        self.assertEqual(response[0]["description"], "A tile used for testing")
        self.assertEqual(response[0]["icon"], "testicon")

    def test_get_tile(self):
        response = self.api_session.get("/@tiles/sample.tile")

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["title"], "Sample tile")
        self.assertEqual(response["properties"]["title"]["title"], "Title")
        self.assertEqual(response["properties"]["title"]["type"], "string")
