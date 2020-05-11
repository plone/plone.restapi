# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import HAS_AT
from plone.restapi.testing import PLONE_RESTAPI_AT_INTEGRATION_TESTING
from plone.restapi.tests.test_expansion import ExpandableElementFoo
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

import json
import unittest


class TestATContentSerializer(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        if not HAS_AT:
            raise unittest.SkipTest("Skip tests if Archetypes is not present")
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "ATTestDocument", id="doc1", title="Test Document"
            )
        ]

        self.doc1.setCreationDate(DateTime("2016-01-21T01:14:48+00:00"))
        self.doc1.setModificationDate(DateTime("2016-01-21T01:24:11+00:00"))
        self.doc1._setUID("76644b6611ab44c6881efd9cb17db12e")

    def serialize(self, obj):
        serializer = getMultiAdapter((obj, self.request), ISerializeToJson)
        return serializer()

    def test_serializer_returns_json_serializeable_object(self):
        obj = self.serialize(self.doc1)
        self.assertTrue(isinstance(json.dumps(obj), str), "Not JSON serializable")

    @unittest.skip("We do not include the context at this point")
    def test_serializer_includes_context(self):
        obj = self.serialize(self.doc1)
        self.assertIn(u"@context", obj)
        self.assertEqual(u"http://www.w3.org/ns/hydra/context.jsonld", obj[u"@context"])

    def test_serializer_includes_json_ld_id(self):
        obj = self.serialize(self.doc1)
        self.assertIn(u"@id", obj)
        self.assertEqual(self.doc1.absolute_url(), obj[u"@id"])

    def test_serializer_includes_id(self):
        obj = self.serialize(self.doc1)
        self.assertIn(u"id", obj)
        self.assertEqual(self.doc1.id, obj[u"id"])

    def test_serializer_includes_type(self):
        obj = self.serialize(self.doc1)
        self.assertIn(u"@type", obj)
        self.assertEqual(self.doc1.portal_type, obj[u"@type"])

    def test_serializer_includes_review_state(self):
        obj = self.serialize(self.doc1)
        self.assertIn(u"review_state", obj)
        self.assertEqual(u"private", obj[u"review_state"])

    def test_serializer_includes_uid(self):
        obj = self.serialize(self.doc1)
        self.assertIn(u"UID", obj)
        self.assertEqual(u"76644b6611ab44c6881efd9cb17db12e", obj[u"UID"])

    def test_serializer_includes_creation_date(self):
        obj = self.serialize(self.doc1)
        self.assertIn(u"creation_date", obj)
        self.assertEqual(u"2016-01-21T01:14:48+00:00", obj[u"creation_date"])

    def test_serializer_includes_modification_date(self):
        obj = self.serialize(self.doc1)
        self.assertIn(u"modification_date", obj)
        self.assertEqual(u"2016-01-21T01:24:11+00:00", obj[u"modification_date"])

    def test_serializer_ignores_field_without_read_permission(self):
        self.doc1.setTestReadPermissionField(u"Secret Stuff")
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        self.assertNotIn(u"testReadPermissionField", self.serialize(self.doc1))

    def test_serializer_ignores_writeonly_field(self):
        self.doc1.setTestWriteonlyField(u"Secret Stuff")
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        self.assertNotIn(u"testWriteonlyField", self.serialize(self.doc1))

    def test_serializer_includes_folder_items(self):
        folder = self.portal[
            self.portal.invokeFactory("ATTestFolder", id="folder", title="Test Folder")
        ]
        folder.invokeFactory("ATTestFolder", id="subfolder", title="Subfolder")
        folder.invokeFactory("ATTestDocument", id="doc", title="A Document")
        obj = self.serialize(folder)
        self.assertIn("items", obj)
        self.assertDictEqual(
            {
                "@id": "http://nohost/plone/folder/subfolder",
                "@type": "ATTestFolder",
                "description": "",
                "title": u"Subfolder",
                "review_state": "private",
            },
            obj["items"][0],
        )
        self.assertDictEqual(
            {
                "@id": "http://nohost/plone/folder/doc",
                "@type": "ATTestDocument",
                "description": "",
                "title": u"A Document",
                "review_state": "private",
            },
            obj["items"][1],
        )

    def test_serializer_orders_folder_items_by_get_object_position_in_parent(
        self,
    ):  # noqa
        folder = self.portal[
            self.portal.invokeFactory("ATTestFolder", id="folder", title="Test Folder")
        ]
        folder.invokeFactory("ATTestDocument", id="doc1", title="A Document")
        folder.invokeFactory("ATTestDocument", id="doc2", title="Second doc")

        # Change GOPIP (getObjectPositionInParent) based order
        folder.moveObjectsUp("doc2")

        obj = self.serialize(folder)

        self.assertIn("items", obj)
        self.assertEqual(
            obj["items"],
            [
                {
                    "@id": "http://nohost/plone/folder/doc2",
                    "@type": "ATTestDocument",
                    "description": "",
                    "title": u"Second doc",
                    "review_state": "private",
                },
                {
                    "@id": "http://nohost/plone/folder/doc1",
                    "@type": "ATTestDocument",
                    "description": "",
                    "title": u"A Document",
                    "review_state": "private",
                },
            ],
        )

    def test_get_layout(self):
        current_layout = self.doc1.getLayout()
        obj = self.serialize(self.doc1)
        self.assertIn("layout", obj)
        self.assertEqual(current_layout, obj["layout"])

    def test_serializer_includes_expansion(self):
        provideAdapter(
            ExpandableElementFoo,
            adapts=(Interface, IBrowserRequest),
            provides=IExpandableElement,
            name="foo",
        )
        obj = self.serialize(self.doc1)
        self.assertIn("foo", obj["@components"])
        self.assertEqual("collapsed", obj["@components"]["foo"])
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(
            ExpandableElementFoo,
            (Interface, IBrowserRequest),
            IExpandableElement,
            "foo",
        )

    def test_get_is_folderish_in_folder(self):
        self.portal.invokeFactory("Folder", id=u"folder")
        serializer = getMultiAdapter(
            (self.portal.folder, self.request), ISerializeToJson
        )
        obj = serializer()
        self.assertIn("is_folderish", obj)
        self.assertEqual(True, obj["is_folderish"])

    def test_nextprev_no_nextprev(self):
        folder = api.content.create(
            container=self.portal,
            type="ATTestFolder",
            title="Folder with items",
            description="This is a folder with some documents",
        )
        doc = api.content.create(
            container=folder,
            type="ATTestDocument",
            title="Item 1",
            description="One item alone in the folder",
        )
        data = self.serialize(doc)
        self.assertEqual({}, data["previous_item"])
        self.assertEqual({}, data["next_item"])

    def test_nextprev_has_prev(self):
        folder = api.content.create(
            container=self.portal,
            type="ATTestFolder",
            title="Folder with items",
            description="This is a folder with some documents",
        )
        api.content.create(
            container=folder,
            type="ATTestDocument",
            title="Item 1",
            description="Previous item",
        )
        doc = api.content.create(
            container=folder,
            type="ATTestDocument",
            title="Item 2",
            description="Current item",
        )
        data = self.serialize(doc)
        self.assertEqual(
            {
                "@id": "http://nohost/plone/folder-with-items/item-1",
                "@type": "ATTestDocument",
                "title": "Item 1",
                "description": "Previous item",
            },
            data["previous_item"],
        )
        self.assertEqual({}, data["next_item"])

    def test_nextprev_has_next(self):
        folder = api.content.create(
            container=self.portal,
            type="ATTestFolder",
            title="Folder with items",
            description="This is a folder with some documents",
        )
        doc = api.content.create(
            container=folder,
            type="ATTestDocument",
            title="Item 1",
            description="Current item",
        )
        api.content.create(
            container=folder,
            type="ATTestDocument",
            title="Item 2",
            description="Next item",
        )
        data = self.serialize(doc)
        self.assertEqual({}, data["previous_item"])
        self.assertEqual(
            {
                "@id": "http://nohost/plone/folder-with-items/item-2",
                "@type": "ATTestDocument",
                "title": "Item 2",
                "description": "Next item",
            },
            data["next_item"],
        )

    def test_nextprev_has_nextprev(self):
        folder = api.content.create(
            container=self.portal,
            type="ATTestFolder",
            title="Folder with items",
            description="This is a folder with some documents",
        )
        api.content.create(
            container=folder,
            type="ATTestDocument",
            title="Item 1",
            description="Previous item",
        )
        doc = api.content.create(
            container=folder,
            type="ATTestDocument",
            title="Item 2",
            description="Current item",
        )
        api.content.create(
            container=folder,
            type="ATTestDocument",
            title="Item 3",
            description="Next item",
        )
        data = self.serialize(doc)
        self.assertEqual(
            {
                "@id": "http://nohost/plone/folder-with-items/item-1",
                "@type": "ATTestDocument",
                "title": "Item 1",
                "description": "Previous item",
            },
            data["previous_item"],
        )
        self.assertEqual(
            {
                "@id": "http://nohost/plone/folder-with-items/item-3",
                "@type": "ATTestDocument",
                "title": "Item 3",
                "description": "Next item",
            },
            data["next_item"],
        )

    def test_nextprev_root_no_nextprev(self):
        data = self.serialize(self.doc1)
        self.assertEqual({}, data["previous_item"])
        self.assertEqual({}, data["next_item"])

    def test_nextprev_root_has_prev(self):
        doc = api.content.create(
            container=self.portal,
            type="ATTestDocument",
            title="Item 2",
            description="Current item",
        )
        data = self.serialize(doc)
        self.assertEqual(
            {
                "@id": "http://nohost/plone/doc1",
                "@type": "ATTestDocument",
                "title": "Test Document",
                "description": "",
            },
            data["previous_item"],
        )
        self.assertEqual({}, data["next_item"])

    def test_nextprev_root_has_next(self):
        api.content.create(
            container=self.portal,
            type="ATTestDocument",
            title="Item 2",
            description="Next item",
        )
        data = self.serialize(self.doc1)
        self.assertEqual({}, data["previous_item"])
        self.assertEqual(
            {
                "@id": "http://nohost/plone/item-2",
                "@type": "ATTestDocument",
                "title": "Item 2",
                "description": "Next item",
            },
            data["next_item"],
        )

    def test_nextprev_root_has_nextprev(self):
        api.content.create(
            container=self.portal,
            type="ATTestDocument",
            title="Item 1",
            description="Previous item",
        )
        doc = api.content.create(
            container=self.portal,
            type="ATTestDocument",
            title="Item 2",
            description="Current item",
        )
        api.content.create(
            container=self.portal,
            type="ATTestDocument",
            title="Item 3",
            description="Next item",
        )
        data = self.serialize(doc)
        self.assertEqual(
            {
                "@id": "http://nohost/plone/item-1",
                "@type": "ATTestDocument",
                "title": "Item 1",
                "description": "Previous item",
            },
            data["previous_item"],
        )
        self.assertEqual(
            {
                "@id": "http://nohost/plone/item-3",
                "@type": "ATTestDocument",
                "title": "Item 3",
                "description": "Next item",
            },
            data["next_item"],
        )
