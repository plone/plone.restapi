# -*- coding: utf-8 -*-
from pkg_resources import get_distribution
from pkg_resources import parse_version
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest

zcatalog_version = get_distribution("Products.ZCatalog").version
if parse_version(zcatalog_version) >= parse_version("5.1"):
    SUPPORT_NOT_UUID_QUERIES = True
else:
    SUPPORT_NOT_UUID_QUERIES = False


class TestQuerystringSearchEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.portal.invokeFactory("Document", "testdocument", title="Test Document")
        self.doc = self.portal.testdocument

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_querystringsearch_basic(self):
        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.is",
                        "v": ["Document"],
                    }
                ]
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIn("items_total", response.json())
        self.assertEqual(response.json()["items_total"], 1)
        self.assertEqual(len(response.json()["items"]), 1)
        self.assertNotIn("effective", response.json()["items"][0])

    def test_querystringsearch_fullobjects(self):
        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.is",
                        "v": ["Document"],
                    }
                ],
                "fullobjects": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIn("items_total", response.json())
        self.assertIn("effective", response.json()["items"][0])
        self.assertEqual(response.json()["items_total"], 1)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_querystringsearch_complex(self):

        for a in range(1, 10):
            self.portal.invokeFactory(
                "Document", "testdocument" + str(a), title="Test Document " + str(a)
            )
            self.doc = self.portal.testdocument

        transaction.commit()

        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.is",
                        "v": ["Document"],
                    }
                ],
                "b_size": 5,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIn("items_total", response.json())
        self.assertEqual(response.json()["items_total"], 10)
        self.assertEqual(len(response.json()["items"]), 5)
        self.assertNotIn("effective", response.json()["items"][0])
        self.assertEqual(response.json()["items"][4]["title"], u"Test Document 4")

        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.is",
                        "v": ["Document"],
                    }
                ],
                "b_size": 5,
                "b_start": 5,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIn("items_total", response.json())
        self.assertEqual(response.json()["items_total"], 10)
        self.assertEqual(len(response.json()["items"]), 5)
        self.assertNotIn("effective", response.json()["items"][0])
        self.assertEqual(response.json()["items"][4]["title"], u"Test Document 9")

    @unittest.skipIf(
        not SUPPORT_NOT_UUID_QUERIES,
        "Skipping because ZCatalog allows not queries on UUIDIndex from >=5.1",
    )
    def test_querystringsearch_do_not_return_context(self):
        self.portal.invokeFactory("Document", "testdocument2", title="Test Document 2")
        self.doc = self.portal.testdocument

        transaction.commit()

        response = self.api_session.post(
            "/testdocument/@querystring-search",
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.is",
                        "v": ["Document"],
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items_total"], 1)
        self.assertEqual(
            response.json()["items"][0]["@id"],
            "{}/testdocument2".format(self.portal.absolute_url()),
        )
