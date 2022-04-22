"""
Test Rest API endpoints for retrieving ZODB database details.
"""

from plone.restapi import testing
from Products.CMFCore.utils import getToolByName


class TestDatabaseServiceFunctional(testing.PloneRestAPIBrowserTestCase):
    """
    Test Rest API endpoints for retrieving ZODB database details.
    """

    def setUp(self):
        """
        Capture references useful for testing.
        """
        super().setUp()

        self.catalog = getToolByName(self.portal, "portal_catalog")

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
