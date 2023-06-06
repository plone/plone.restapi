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

        self.api_session = RelativeSession(self.portal_url, test=self)
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

    def test_querystringsearch_basic_get(self):
        self.portal.invokeFactory("Document", "doc2", title="Test Document 2")
        transaction.commit()

        response = self.api_session.get(
            "/@querystring-search?query=%7B%22query%22%3A%20%5B%7B%22i%22%3A%20%22portal_type%22%2C%20%22o%22%3A%20%22plone.app.querystring.operation.selection.any%22%2C%20%22v%22%3A%20%5B%22Document%22%5D%7D%5D%2C%20%22b_size%22%3A%201%7D"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIn("items_total", response.json())
        self.assertEqual(response.json()["items_total"], 2)
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

    def test_querystringsearch_metadata_fields_post(self):
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
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIn("items_total", response.json())
        self.assertNotIn("effective", response.json()["items"][0])

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
                "metadata_fields": ["effective"],
            },
        )

        self.assertIn("effective", response.json()["items"][0])

    def test_querystringsearch_metadata_fields_get(self):

        response = self.api_session.get(
            "/@querystring-search?query=%7B%22query%22%3A%20%5B%7B%22i%22%3A%20%22portal_type%22%2C%20%22o%22%3A%20%22plone.app.querystring.operation.selection.is%22%2C%20%22v%22%3A%20%5B%22Document%22%5D%7D%5D%7D"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIn("items_total", response.json())
        self.assertNotIn("effective", response.json()["items"][0])

        # request with metadata_fields
        response = self.api_session.get(
            "/@querystring-search?query=%7B%22query%22%3A%20%5B%7B%22i%22%3A%20%22portal_type%22%2C%20%22o%22%3A%20%22plone.app.querystring.operation.selection.is%22%2C%20%22v%22%3A%20%5B%22Document%22%5D%7D%5D%2C%20%22metadata_fields%22%3A%20%5B%22effective%22%5D%7D"
        )

        self.assertIn("effective", response.json()["items"][0])

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
                "sort_on": "sortable_title",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIn("items_total", response.json())
        self.assertEqual(response.json()["items_total"], 10)
        self.assertEqual(len(response.json()["items"]), 5)
        self.assertNotIn("effective", response.json()["items"][0])
        self.assertEqual(response.json()["items"][4]["title"], "Test Document 4")

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
                "sort_on": "sortable_title",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.json())
        self.assertIn("items_total", response.json())
        self.assertEqual(response.json()["items_total"], 10)
        self.assertEqual(len(response.json()["items"]), 5)
        self.assertNotIn("effective", response.json()["items"][0])
        self.assertEqual(response.json()["items"][4]["title"], "Test Document 9")

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
            f"{self.portal.absolute_url()}/testdocument2",
        )

    def test_querystringsearch_sort(self):
        # id: testdocument1, title: Test I Document 1
        # id: testdocument2, title: Test H Document 2
        # ...
        # id: testdocument9, title: Test A Document 9
        for a in range(1, 10):
            self.portal.invokeFactory(
                "Document",
                "testdocument" + str(a),
                title="Test " + "ABCDEFGHI"[-a] + " Document " + str(a),
            )
        transaction.commit()

        query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["Document"],
            }
        ]
        # default order 'ascending'
        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": query,
                "sort_on": "sortable_title",
            },
        )
        self.assertEqual(response.json()["items_total"], 10)
        self.assertEqual(
            response.json()["items"][0]["title"],
            "Test A Document 9",
        )
        self.assertEqual(
            response.json()["items"][-1]["title"],
            "Test I Document 1",
        )

        # force order 'ascending'
        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": query,
                "sort_on": "sortable_title",
                "sort_order": "ascending",
            },
        )
        self.assertEqual(response.json()["items_total"], 10)
        self.assertEqual(
            response.json()["items"][0]["title"],
            "Test A Document 9",
        )
        self.assertEqual(
            response.json()["items"][-1]["title"],
            "Test I Document 1",
        )

        # force order 'descending'
        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": query,
                "sort_on": "sortable_title",
                "sort_order": "descending",
            },
        )
        self.assertEqual(response.json()["items_total"], 10)
        self.assertEqual(
            response.json()["items"][0]["title"],
            "Test I Document 1",
        )
        self.assertEqual(
            response.json()["items"][-1]["title"],
            "Test A Document 9",
        )

        # sort by id, 'ascending'
        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": query,
                "sort_on": "getId",
                "sort_order": "ascending",
            },
        )
        self.assertEqual(response.json()["items_total"], 10)
        self.assertEqual(
            response.json()["items"][0]["@id"],
            f"{self.portal.absolute_url()}/testdocument",
        )
        self.assertEqual(
            response.json()["items"][-1]["@id"],
            f"{self.portal.absolute_url()}/testdocument9",
        )

    def test_querystringsearch__bad_json(self):
        response = self.api_session.get("/@querystring-search?query={")
        self.assertEqual(response.status_code, 400)

    def test_querystringsearch__empty_query(self):
        response = self.api_session.post(
            "/@querystring-search",
            json={"query": []},
        )
        self.assertEqual(response.status_code, 400)

    def test_querystringsearch__bad_b_size(self):
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
                "b_size": "x",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_querystringsearch__bad_operation(self):
        response = self.api_session.post(
            "/@querystring-search",
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "BOGUS",
                        "v": ["Document"],
                    }
                ],
            },
        )
        self.assertEqual(response.status_code, 400)
