from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

import requests
import transaction
import unittest

try:
    from Products.CMFPlone.relationhelper import get_relations_stats
except ImportError:
    try:
        from collective.relationhelpers.api import get_relations_stats
    except ImportError:
        get_relations_stats = None


class TestRelationsEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, SITE_OWNER_NAME)
        self.doc1 = api.content.create(
            container=self.portal,
            type="Document",
            id="document",
            title="Document 1",
        )
        self.doc2 = api.content.create(
            container=self.portal,
            type="Document",
            id="document-2",
            title="Document 2",
        )
        self.doc3 = api.content.create(
            container=self.portal,
            type="Document",
            id="document-3",
            title="Document 3",
        )
        api.content.transition(self.doc1, "publish")
        api.content.transition(self.doc2, "publish")
        # doc3 stays private

        transaction.commit()

    def test_get_stats(self):
        if get_relations_stats:
            response = requests.get(
                self.portal.absolute_url() + "/@relations",
                headers={"Accept": "application/json"},
                auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            )

            self.assertEqual(response.status_code, 200)
            resp = response.json()
            self.assertIn("relations", resp)
            self.assertIn("broken", resp)

    def test_query_relations(self):
        if get_relations_stats:
            response = requests.get(
                self.portal.absolute_url() + "/@relations?source=/document",
                headers={"Accept": "application/json"},
                auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            )

            self.assertEqual(response.status_code, 200)
            resp = response.json()
            self.assertEqual(resp, {"foo": "bar"})


# TODO relations: tests (if get_relations_stats)
