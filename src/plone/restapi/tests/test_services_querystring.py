from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import unittest


class TestQuerystringEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_endpoint_lists_indexes(self):
        response = self.api_session.get("/@querystring")

        self.assertEqual(response.status_code, 200)
        self.assertIn("indexes", response.json())
        self.assertIn("isFolderish", response.json()["indexes"])

    def test_endpoint_lists_sortable_indexes(self):
        response = self.api_session.get("/@querystring")

        self.assertEqual(response.status_code, 200)
        self.assertIn("sortable_indexes", response.json())
        self.assertIn("sortable_title", response.json()["sortable_indexes"])

    def test_endpoint_shows_field_config(self):
        response = self.api_session.get("/@querystring")

        self.assertEqual(response.status_code, 200)
        indexes = response.json()["indexes"]
        idx = indexes["Title"]

        expected_field_config = {
            "description": "Text search of an item's title",
            "enabled": True,
            "group": "Text",
            "operations": ["plone.app.querystring.operation.string.contains"],
            "operators": {
                "plone.app.querystring.operation.string.contains": {
                    "description": None,
                    "operation": "plone.app.querystring.queryparser._contains",
                    "title": "Contains",
                    "widget": "StringWidget",
                }
            },
            "sortable": False,
            "title": "Title",
            "values": {},
            "vocabulary": None,
        }
        self.assertEqual(expected_field_config, idx)

    def test_endpoint_inlines_vocabularies(self):
        response = self.api_session.get("/@querystring")

        self.assertEqual(response.status_code, 200)
        indexes = response.json()["indexes"]
        idx = indexes["review_state"]

        self.assertDictContainsSubset(
            {
                "title": "Review state",
                "vocabulary": "plone.app.vocabularies.WorkflowStates",
            },
            idx,
        )

        expected_vocab_values = {
            "external": {"title": "Externally visible [external]"},
            "internal": {"title": "Internal draft [internal]"},
            "internally_published": {
                "title": "Internally published [internally_published]"
            },
            "pending": {"title": "Pending [pending]"},
            "private": {"title": "Private [private]"},
            "published": {"title": "Published with accent \xe9 [published]"},
            "visible": {"title": "Public draft [visible]"},
        }
        self.assertTrue(
            all(elem in idx["values"].items() for elem in expected_vocab_values.items())
        )

    def test_endpoint_inlines_operators(self):
        response = self.api_session.get("/@querystring")

        self.assertEqual(response.status_code, 200)
        indexes = response.json()["indexes"]
        idx = indexes["isDefaultPage"]

        self.assertDictContainsSubset(
            {
                "title": "Default Page",
                "operations": [
                    "plone.app.querystring.operation.boolean.isTrue",
                    "plone.app.querystring.operation.boolean.isFalse",
                ],
            },
            idx,
        )

        expected_operators = {
            "plone.app.querystring.operation.boolean.isFalse": {
                "description": None,
                "operation": "plone.app.querystring.queryparser._isFalse",
                "title": "No",
                "widget": None,
            },
            "plone.app.querystring.operation.boolean.isTrue": {
                "description": None,
                "operation": "plone.app.querystring.queryparser._isTrue",
                "title": "Yes",
                "widget": None,
            },
        }
        self.assertEqual(expected_operators, idx["operators"])

    def test_endpoint_includes_widgets_for_operators(self):
        response = self.api_session.get("/@querystring")

        self.assertEqual(response.status_code, 200)
        indexes = response.json()["indexes"]
        idx = indexes["getObjPositionInParent"]

        self.assertDictContainsSubset(
            {
                "title": "Order in folder",
                "operations": [
                    "plone.app.querystring.operation.int.is",
                    "plone.app.querystring.operation.int.lessThan",
                    "plone.app.querystring.operation.int.largerThan",
                ],
            },
            idx,
        )

        ops = idx["operators"]

        self.assertEqual(
            {
                "description": None,
                "operation": "plone.app.querystring.queryparser._intLargerThan",
                "title": "Larger than",
                "widget": "StringWidget",
            },
            ops["plone.app.querystring.operation.int.largerThan"],
        )
