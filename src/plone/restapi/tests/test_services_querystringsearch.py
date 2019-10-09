# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


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
        self.assertEquals(response.json()["items_total"], 1)
        self.assertEquals(len(response.json()["items"]), 1)
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
        self.assertEquals(response.json()["items_total"], 1)
        self.assertEquals(len(response.json()["items"]), 1)

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
        self.assertEquals(response.json()["items_total"], 10)
        self.assertEquals(len(response.json()["items"]), 5)
        self.assertNotIn("effective", response.json()["items"][0])
        self.assertEquals(response.json()["items"][4]["title"], u"Test Document 4")

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
        self.assertEquals(response.json()["items_total"], 10)
        self.assertEquals(len(response.json()["items"]), 5)
        self.assertNotIn("effective", response.json()["items"][0])
        self.assertEquals(response.json()["items"][4]["title"], u"Test Document 9")
