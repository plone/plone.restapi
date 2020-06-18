# -*- coding: utf-8 -*-
from DateTime import DateTime
from mock import patch
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
from plone.namedfile.file import NamedFile
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.scale import storage
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

import json
import os
import unittest


class TestSerializeToJsonAdapter(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.workflowTool = getToolByName(self.portal, "portal_workflow")
        self.portal_url = self.portal.absolute_url()
        self.portal.invokeFactory("Document", id="doc1", title="Document 1")
        self.portal.invokeFactory(
            "DXTestDocument", id="dxdoc", title="DX Test Document"
        )

    def serialize(self, obj, fullobjects=False):
        if fullobjects:
            self.request.form["fullobjects"] = 1

        serializer = getMultiAdapter((obj, self.request), ISerializeToJson)
        return serializer()

    def test_serialize_returns_id(self):
        self.assertEqual(
            self.serialize(self.portal.doc1)["@id"], self.portal_url + "/doc1"
        )

    def test_serialize_returns_type(self):
        self.assertTrue(
            self.serialize(self.portal.doc1).get("@type"),
            "The @type attribute should be present.",
        )
        self.assertEqual(self.serialize(self.portal.doc1)["@type"], u"Document")

    def test_serialize_returns_title(self):
        self.assertEqual(self.serialize(self.portal.doc1)["title"], u"Document 1")

    def test_serialize_can_read_as_manager(self):
        self.portal.dxdoc.test_read_permission_field = u"Test Read Permission"
        self.workflowTool.doActionFor(self.portal.dxdoc, "publish")
        setRoles(self.portal, TEST_USER_ID, ["Member", "Manager"])
        self.assertIn(
            "Test Read Permission", list(self.serialize(self.portal.dxdoc).values())
        )

    def test_serialize_cannot_read_as_member(self):
        self.portal.dxdoc.test_read_permission_field = u"Test Read Permission"
        self.workflowTool.doActionFor(self.portal.dxdoc, "publish")
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        self.assertNotIn(
            "Test Read Permission", list(self.serialize(self.portal.dxdoc).values())
        )

    def test_serialize_returns_desciption(self):
        self.portal.doc1.description = u"This is a document"
        self.assertEqual(
            self.serialize(self.portal.doc1)["description"], u"This is a document"
        )

    def test_serialize_returns_rich_text(self):
        self.portal.doc1.text = RichTextValue(
            u"Lorem ipsum.", "text/plain", "text/html"
        )
        self.assertEqual(
            self.serialize(self.portal.doc1).get("text"),
            {
                u"data": u"<p>Lorem ipsum.</p>",
                u"content-type": u"text/plain",
                u"encoding": u"utf-8",
            },
        )

    def test_serialize_returns_effective(self):
        self.portal.doc1.setEffectiveDate(DateTime("2014/04/04"))
        self.assertEqual(
            self.serialize(self.portal.doc1)["effective"], "2014-04-04T00:00:00"
        )

    def test_serialize_returns_expires(self):
        self.portal.doc1.setExpirationDate(DateTime("2017/01/01"))
        self.assertEqual(
            self.serialize(self.portal.doc1)["expires"], "2017-01-01T00:00:00"
        )

    def test_serialize_on_folder_returns_items_attr(self):
        self.portal.invokeFactory("Folder", id="folder1", title="Folder 1")
        self.portal.folder1.invokeFactory("Document", id="doc1")
        self.portal.folder1.doc1.title = u"Document 1"
        self.portal.folder1.doc1.description = u"This is a document"
        self.portal.folder1.doc1.reindexObject()
        self.assertEqual(
            self.serialize(self.portal.folder1)["items"],
            [
                {
                    u"@id": u"http://nohost/plone/folder1/doc1",
                    u"@type": u"Document",
                    u"description": u"This is a document",
                    u"title": u"Document 1",
                    u"review_state": u"private",
                }
            ],
        )

    def test_serialize_folder_orders_items_by_get_object_position_in_parent(
        self,
    ):  # noqa
        self.portal.invokeFactory("Folder", id="folder1", title="Folder 1")
        self.portal.folder1.invokeFactory("Document", id="doc1")
        self.portal.folder1.doc1.title = u"Document 1"
        self.portal.folder1.doc1.description = u"This is a document"
        self.portal.folder1.doc1.reindexObject()

        self.portal.folder1.invokeFactory("Document", id="doc2")
        self.portal.folder1.doc2.title = u"Document 2"
        self.portal.folder1.doc2.description = u"Second doc"
        self.portal.folder1.doc2.reindexObject()

        # Change GOPIP (getObjectPositionInParent) based order
        self.portal.folder1.moveObjectsUp("doc2")

        self.assertEqual(
            self.serialize(self.portal.folder1)["items"],
            [
                {
                    u"@id": u"http://nohost/plone/folder1/doc2",
                    u"@type": u"Document",
                    u"description": u"Second doc",
                    u"title": u"Document 2",
                    u"review_state": u"private",
                },
                {
                    u"@id": u"http://nohost/plone/folder1/doc1",
                    u"@type": u"Document",
                    u"description": u"This is a document",
                    u"title": u"Document 1",
                    u"review_state": u"private",
                },
            ],
        )

    def test_serialize_returns_parent(self):
        self.assertTrue(
            self.serialize(self.portal.doc1).get("parent"),
            "The parent attribute should be present.",
        )
        self.assertEqual(
            {
                "@id": self.portal.absolute_url(),
                "@type": self.portal.portal_type,
                "title": self.portal.title,
                "description": self.portal.description,
            },
            self.serialize(self.portal.doc1)["parent"],
        )

    def test_serialize_does_not_returns_parent_on_root(self):
        self.assertEqual(
            {},
            self.serialize(self.portal).get("parent"),
            "The parent attribute should be present, even on portal root.",
        )
        self.assertEqual(
            {
                "@id": self.portal.absolute_url(),
                "@type": self.portal.portal_type,
                "title": self.portal.title,
                "description": self.portal.description,
            },
            self.serialize(self.portal.doc1)["parent"],
            "The parent attribute on portal root should be None",
        )

    def test_serialize_returns_site_root_type(self):
        self.assertTrue(
            self.serialize(self.portal).get("@type"),
            "The @type attribute should be present.",
        )
        self.assertEqual(self.serialize(self.portal)["@type"], u"Plone Site")

    def test_serialize_site_orders_items_by_get_object_position_in_parent(self):  # noqa
        # Change GOPIP (getObjectPositionInParent) based order
        self.portal.moveObjectsUp("dxdoc")

        self.assertEqual(
            self.serialize(self.portal)["items"],
            [
                {
                    u"@id": u"http://nohost/plone/dxdoc",
                    u"@type": u"DXTestDocument",
                    u"description": u"",
                    u"title": u"DX Test Document",
                    u"review_state": u"private",
                },
                {
                    u"@id": u"http://nohost/plone/doc1",
                    u"@type": u"Document",
                    u"description": u"",
                    u"title": u"Document 1",
                    u"review_state": u"private",
                },
            ],
        )

    def test_serialize_ignores_underscore_values(self):
        self.assertFalse("__name__" in self.serialize(self.portal.doc1))
        self.assertFalse("manage_options" in self.serialize(self.portal.doc1))

    def test_serialize_file(self):
        self.portal.invokeFactory("File", id="file1", title="File 1")
        self.portal.file1.file = NamedFile(
            data=u"Spam and eggs", contentType=u"text/plain", filename=u"test.txt"
        )

        file_url = self.portal.file1.absolute_url()
        download_url = "{0}/@@download/file".format(file_url)
        self.assertEqual(
            {
                u"filename": u"test.txt",
                u"content-type": u"text/plain",
                u"download": download_url,
                u"size": 13,
            },
            self.serialize(self.portal.file1).get("file"),
        )

    def test_serialize_empty_file_returns_none(self):
        self.portal.invokeFactory("File", id="file1", title="File 1")

        self.assertEqual(None, self.serialize(self.portal.file1).get("file"))

    def test_serialize_image(self):
        self.portal.invokeFactory("Image", id="image1", title="Image 1")
        image_file = os.path.join(os.path.dirname(__file__), u"image.png")
        with open(image_file, "rb") as f:
            image_data = f.read()
        self.portal.image1.image = NamedBlobImage(
            data=image_data, contentType="image/png", filename=u"image.png"
        )

        self.maxDiff = 99999

        with patch.object(storage, "uuid4", return_value="uuid_1"):
            obj_url = self.portal.image1.absolute_url()
            scale_url_uuid = "uuid_1"
            download_url = u"{}/@@images/{}.png".format(obj_url, scale_url_uuid)
            scales = {
                u"listing": {u"download": download_url, u"width": 16, u"height": 4},
                u"icon": {u"download": download_url, u"width": 32, u"height": 8},
                u"tile": {u"download": download_url, u"width": 64, u"height": 16},
                u"thumb": {u"download": download_url, u"width": 128, u"height": 33},
                u"mini": {u"download": download_url, u"width": 200, u"height": 52},
                u"preview": {u"download": download_url, u"width": 215, u"height": 56},
                u"large": {u"download": download_url, u"width": 215, u"height": 56},
            }
            self.assertEqual(
                {
                    u"filename": u"image.png",
                    u"content-type": u"image/png",
                    u"size": 1185,
                    u"download": download_url,
                    u"width": 215,
                    u"height": 56,
                    u"scales": scales,
                },
                self.serialize(self.portal.image1)["image"],
            )

    def test_serialize_empty_image_returns_none(self):
        self.portal.invokeFactory("Image", id="image1", title="Image 1")
        self.assertEqual(None, self.serialize(self.portal.image1)["image"])

    def test_serialize_to_json_collection(self):
        self.portal.invokeFactory("Collection", id="collection1")
        self.portal.collection1.title = "My Collection"
        self.portal.collection1.description = u"This is a collection with two documents"
        self.portal.collection1.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.string.is",
                "v": "Document",
            }
        ]
        self.portal.invokeFactory("Document", id="doc2", title="Document 2")
        self.portal.doc1.reindexObject()
        self.portal.doc2.reindexObject()

        self.assertEqual(
            u"Collection", self.serialize(self.portal.collection1).get("@type")
        )
        self.assertEqual(
            u"Collection", self.serialize(self.portal.collection1).get("@type")
        )
        self.assertEqual(
            [
                {
                    u"@id": self.portal.doc1.absolute_url(),
                    u"@type": u"Document",
                    u"description": u"",
                    u"title": u"Document 1",
                    u"review_state": u"private",
                },
                {
                    u"@id": self.portal.doc2.absolute_url(),
                    u"@type": u"Document",
                    u"description": u"",
                    u"title": u"Document 2",
                    u"review_state": u"private",
                },
            ],
            self.serialize(self.portal.collection1).get("items"),
        )

    def test_serialize_to_json_collection_fullobjects(self):
        self.portal.invokeFactory("Collection", id="collection1")
        self.portal.collection1.title = "My Collection"
        self.portal.collection1.description = u"This is a collection with two documents"
        self.portal.collection1.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.string.is",
                "v": "Document",
            }
        ]
        self.portal.invokeFactory("Document", id="doc2", title="Document 2")
        self.portal.doc1.reindexObject()
        self.portal.doc2.reindexObject()

        self.assertEqual(
            u"Collection", self.serialize(self.portal.collection1).get("@type")
        )
        self.assertEqual(
            u"Collection", self.serialize(self.portal.collection1).get("@type")
        )

        items = self.serialize(self.portal.collection1, fullobjects=True).get("items")
        self.assertIn("UID", items[0])
        self.assertEqual(items[0]["id"], self.portal.doc1.getId())

        self.assertIn("UID", items[1])
        self.assertEqual(items[1]["id"], self.portal.doc2.getId())

    def test_serialize_to_json_collection_include_items(self):
        self.portal.invokeFactory("Collection", id="collection1")
        self.portal.collection1.title = "My Collection"
        self.portal.collection1.description = u"This is a collection with two documents"
        self.portal.collection1.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.string.is",
                "v": "Document",
            }
        ]
        self.portal.invokeFactory("Document", id="doc2", title="Document 2")
        self.portal.doc1.reindexObject()
        self.portal.doc2.reindexObject()

        self.assertEqual(
            u"Collection", self.serialize(self.portal.collection1).get("@type")
        )
        self.assertEqual(
            u"Collection", self.serialize(self.portal.collection1).get("@type")
        )

        self.request.form["include_items"] = False
        without_items = self.serialize(self.portal.collection1)
        self.assertFalse("items" in without_items)
        self.assertFalse("items_total" in without_items)

        self.request.form["include_items"] = True
        serialized = self.serialize(self.portal.collection1)
        items = serialized.get("items")
        self.assertEqual(items[0]["title"], self.portal.doc1.Title())
        self.assertEqual(items[1]["title"], self.portal.doc2.Title())
        self.assertEqual(serialized.get("items_total"), 2)

    def test_serialize_returns_site_root_common(self):
        self.assertIn("title", self.serialize(self.portal))
        self.assertIn("description", self.serialize(self.portal))

    def test_serialize_returns_site_root_opt_in_blocks_not_present(self):
        self.assertEqual(self.serialize(self.portal)["blocks"], {})
        self.assertEqual(self.serialize(self.portal)["blocks_layout"], {})

    def test_serialize_returns_site_root_opt_in_blocks_present(self):
        blocks = {
            "0358abe2-b4f1-463d-a279-a63ea80daf19": {"@type": "description"},
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
        }
        blocks_layout = {
            "items": [
                "07c273fc-8bfc-4e7d-a327-d513e5a945bb",
                "0358abe2-b4f1-463d-a279-a63ea80daf19",
            ]
        }
        self.portal.manage_addProperty("blocks", json.dumps(blocks), "string")
        self.portal.manage_addProperty(
            "blocks_layout", json.dumps(blocks_layout), "string"
        )

        self.assertEqual(self.serialize(self.portal)["blocks"], blocks)
        self.assertEqual(self.serialize(self.portal)["blocks_layout"], blocks_layout)
