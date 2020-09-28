# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import HAS_AT
from plone.restapi.testing import PLONE_RESTAPI_AT_INTEGRATION_TESTING
from zope.component import getMultiAdapter

import unittest


class TestATContentSerializer(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        if not HAS_AT:
            raise unittest.SkipTest("Skip tests if Archetypes is not present")
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "Collection", id="collection", title="Test Collection"
            )
        ]

        self.doc1.setCreationDate(DateTime("2016-01-21T01:14:48+00:00"))
        self.doc1.setModificationDate(DateTime("2016-01-21T01:24:11+00:00"))
        self.doc1._setUID("76644b6611ab44c6881efd9cb17db12e")
        query_data = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["ATTestFolder"],
            },
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.path",
                "v": "/plone/folder",
            },
        ]

        self.doc1.setQuery(query_data)
        self.doc1.setSort_on("created")

    def serialize(self, obj, fullobjects=False):
        if fullobjects:
            self.request.form["fullobjects"] = 1

        serializer = getMultiAdapter((obj, self.request), ISerializeToJson)
        return serializer()

    def test_serializer_includes_collection_items(self):
        folder = self.portal[
            self.portal.invokeFactory("ATTestFolder", id="folder", title="Test Folder")
        ]
        folder.invokeFactory("ATTestFolder", id="subfolder-1", title="Subfolder 1")
        folder.invokeFactory("ATTestFolder", id="subfolder-2", title="Subfolder 2")
        folder.invokeFactory("ATTestDocument", id="doc", title="A Document")
        obj = self.serialize(self.doc1)
        self.assertIn("items", obj)
        items = obj["items"]
        items = sorted(items, key=lambda item: item[u"@id"])
        self.assertDictEqual(
            {
                u"@id": u"http://nohost/plone/folder",
                u"@type": u"ATTestFolder",
                u"description": u"",
                u"title": u"Test Folder",
                "review_state": "private",
            },
            items[0],
        )
        self.assertDictEqual(
            {
                u"@id": u"http://nohost/plone/folder/subfolder-1",
                u"@type": u"ATTestFolder",
                u"description": u"",
                u"title": u"Subfolder 1",
                "review_state": "private",
            },
            items[1],
        )
        self.assertDictEqual(
            {
                u"@id": u"http://nohost/plone/folder/subfolder-2",
                u"@type": u"ATTestFolder",
                u"description": u"",
                u"title": u"Subfolder 2",
                "review_state": "private",
            },
            items[2],
        )

    def test_serializer_includes_collection_fullobjects(self):
        """when using the fullobjects parameter, the collection needs to
        serialize its contents with the standard object serializer"""
        folder = self.portal[
            self.portal.invokeFactory("ATTestFolder", id="folder", title="Test Folder")
        ]
        folder.invokeFactory("ATTestFolder", id="subfolder-1", title="Subfolder 1")
        folder.invokeFactory("ATTestFolder", id="subfolder-2", title="Subfolder 2")
        folder.invokeFactory("ATTestDocument", id="doc", title="A Document")
        obj = self.serialize(self.doc1, fullobjects=True)
        self.assertIn("items", obj)
        items = obj["items"]
        items = sorted(items, key=lambda item: item[u"@id"])
        self.assertIn("UID", items[0])
        self.assertEqual(items[0]["id"], "folder")

        self.assertIn("UID", items[1])
        self.assertEqual(items[1]["id"], "subfolder-1")

        self.assertIn("UID", items[2])
        self.assertEqual(items[2]["id"], "subfolder-2")
