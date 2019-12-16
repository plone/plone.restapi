# -*- coding: utf-8 -*-
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
            u"description": u"Text search of an item's title",
            u"enabled": True,
            u"group": u"Text",
            u"operations": [u"plone.app.querystring.operation.string.contains"],
            u"operators": {
                u"plone.app.querystring.operation.string.contains": {
                    u"description": None,
                    u"operation": u"plone.app.querystring.queryparser._contains",
                    u"title": u"Contains",
                    u"widget": u"StringWidget",
                }
            },
            u"sortable": False,
            u"title": u"Title",
            u"values": {},
            u"vocabulary": None,
        }
        self.assertEqual(expected_field_config, idx)

    def test_endpoint_inlines_vocabularies(self):
        response = self.api_session.get("/@querystring")

        self.assertEqual(response.status_code, 200)
        indexes = response.json()["indexes"]
        idx = indexes["review_state"]

        self.assertDictContainsSubset(
            {
                "title": u"Review state",
                "vocabulary": u"plone.app.vocabularies.WorkflowStates",
            },
            idx,
        )

        expected_vocab_values = {
            u"external": {u"title": u"Externally visible [external]"},
            u"internal": {u"title": u"Internal draft [internal]"},
            u"internally_published": {
                u"title": u"Internally published [internally_published]"
            },
            u"pending": {u"title": u"Pending [pending]"},
            u"private": {u"title": u"Private [private]"},
            u"published": {u"title": u"Published with accent \xe9 [published]"},
            u"visible": {u"title": u"Public draft [visible]"},
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
                "title": u"Default Page",
                "operations": [
                    u"plone.app.querystring.operation.boolean.isTrue",
                    u"plone.app.querystring.operation.boolean.isFalse",
                ],
            },
            idx,
        )

        expected_operators = {
            u"plone.app.querystring.operation.boolean.isFalse": {
                u"description": None,
                u"operation": u"plone.app.querystring.queryparser._isFalse",
                u"title": u"No",
                u"widget": None,
            },
            u"plone.app.querystring.operation.boolean.isTrue": {
                u"description": None,
                u"operation": u"plone.app.querystring.queryparser._isTrue",
                u"title": u"Yes",
                u"widget": None,
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
                "title": u"Order in folder",
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
