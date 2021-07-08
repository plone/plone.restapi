from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.CMFCore.utils import getToolByName

import unittest


class TestDatabaseServiceFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST
        self.catalog = getToolByName(self.portal, "portal_catalog")

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_get_system(self):
        response = self.api_session.get("/@database")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        results = response.json()
        self.assertEqual(results["@id"], self.portal.absolute_url() + "/@database")
        self.assertTrue("cache_length" in results.keys())
        self.assertTrue("cache_length_bytes" in results.keys())
        self.assertTrue("cache_detail_length" in results.keys())
        self.assertTrue("cache_size" in results.keys())
        self.assertTrue("database_size" in results.keys())
        self.assertTrue("db_name" in results.keys())
        self.assertTrue("db_size" in results.keys())
