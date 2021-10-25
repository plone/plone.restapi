from DateTime import DateTime
from unittest.mock import patch
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
        self.assertEqual(self.serialize(self.portal.doc1)["@type"], "Document")

    def test_serialize_returns_title(self):
        self.assertEqual(self.serialize(self.portal.doc1)["title"], "Document 1")

    def test_serialize_can_read_as_manager(self):
        self.portal.dxdoc.test_read_permission_field = "Test Read Permission"
        self.workflowTool.doActionFor(self.portal.dxdoc, "publish")
        setRoles(self.portal, TEST_USER_ID, ["Member", "Manager"])
        self.assertIn(
            "Test Read Permission", list(self.serialize(self.portal.dxdoc).values())
        )

    def test_serialize_cannot_read_as_member(self):
        self.portal.dxdoc.test_read_permission_field = "Test Read Permission"
        self.workflowTool.doActionFor(self.portal.dxdoc, "publish")
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        self.assertNotIn(
            "Test Read Permission", list(self.serialize(self.portal.dxdoc).values())
        )

    def test_serialize_returns_desciption(self):
        self.portal.doc1.description = "This is a document"
        self.assertEqual(
            self.serialize(self.portal.doc1)["description"], "This is a document"
        )

    def test_serialize_returns_rich_text(self):
        self.portal.doc1.text = RichTextValue("Lorem ipsum.", "text/plain", "text/html")
        self.assertEqual(
            self.serialize(self.portal.doc1).get("text"),
            {
                "data": "<p>Lorem ipsum.</p>",
                "content-type": "text/plain",
                "encoding": "utf-8",
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
        self.portal.folder1.doc1.title = "Document 1"
        self.portal.folder1.doc1.description = "This is a document"
        self.portal.folder1.doc1.reindexObject()
        self.assertEqual(
            self.serialize(self.portal.folder1)["items"],
            [
                {
                    "@id": "http://nohost/plone/folder1/doc1",
                    "@type": "Document",
                    "description": "This is a document",
                    "title": "Document 1",
                    "review_state": "private",
                }
            ],
        )

    def test_serialize_folder_orders_items_by_get_object_position_in_parent(
        self,
    ):  # noqa
        self.portal.invokeFactory("Folder", id="folder1", title="Folder 1")
        self.portal.folder1.invokeFactory("Document", id="doc1")
        self.portal.folder1.doc1.title = "Document 1"
        self.portal.folder1.doc1.description = "This is a document"
        self.portal.folder1.doc1.reindexObject()

        self.portal.folder1.invokeFactory("Document", id="doc2")
        self.portal.folder1.doc2.title = "Document 2"
        self.portal.folder1.doc2.description = "Second doc"
        self.portal.folder1.doc2.reindexObject()

        # Change GOPIP (getObjectPositionInParent) based order
        self.portal.folder1.moveObjectsUp("doc2")

        self.assertEqual(
            self.serialize(self.portal.folder1)["items"],
            [
                {
                    "@id": "http://nohost/plone/folder1/doc2",
                    "@type": "Document",
                    "description": "Second doc",
                    "title": "Document 2",
                    "review_state": "private",
                },
                {
                    "@id": "http://nohost/plone/folder1/doc1",
                    "@type": "Document",
                    "description": "This is a document",
                    "title": "Document 1",
                    "review_state": "private",
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
        self.assertEqual(self.serialize(self.portal)["@type"], "Plone Site")

    def test_serialize_site_orders_items_by_get_object_position_in_parent(self):  # noqa
        # Change GOPIP (getObjectPositionInParent) based order
        self.portal.moveObjectsUp("dxdoc")

        self.assertEqual(
            self.serialize(self.portal)["items"],
            [
                {
                    "@id": "http://nohost/plone/dxdoc",
                    "@type": "DXTestDocument",
                    "description": "",
                    "title": "DX Test Document",
                    "review_state": "private",
                },
                {
                    "@id": "http://nohost/plone/doc1",
                    "@type": "Document",
                    "description": "",
                    "title": "Document 1",
                    "review_state": "private",
                },
            ],
        )

    def test_serialize_ignores_underscore_values(self):
        self.assertFalse("__name__" in self.serialize(self.portal.doc1))
        self.assertFalse("manage_options" in self.serialize(self.portal.doc1))

    def test_serialize_file(self):
        self.portal.invokeFactory("File", id="file1", title="File 1")
        self.portal.file1.file = NamedFile(
            data="Spam and eggs", contentType="text/plain", filename="test.txt"
        )

        file_url = self.portal.file1.absolute_url()
        download_url = f"{file_url}/@@download/file"
        self.assertEqual(
            {
                "filename": "test.txt",
                "content-type": "text/plain",
                "download": download_url,
                "size": 13,
            },
            self.serialize(self.portal.file1).get("file"),
        )

    def test_serialize_empty_file_returns_none(self):
        self.portal.invokeFactory("File", id="file1", title="File 1")

        self.assertEqual(None, self.serialize(self.portal.file1).get("file"))

    def test_serialize_image(self):
        self.portal.invokeFactory("Image", id="image1", title="Image 1")
        image_file = os.path.join(os.path.dirname(__file__), "image.png")
        with open(image_file, "rb") as f:
            image_data = f.read()
        self.portal.image1.image = NamedBlobImage(
            data=image_data, contentType="image/png", filename="image.png"
        )

        self.maxDiff = 99999

        with patch.object(storage, "uuid4", return_value="uuid_1"):
            obj_url = self.portal.image1.absolute_url()
            scale_url_uuid = "uuid_1"
            download_url = f"{obj_url}/@@images/{scale_url_uuid}.png"
            scales = {
                "listing": {"download": download_url, "width": 16, "height": 4},
                "icon": {"download": download_url, "width": 32, "height": 8},
                "tile": {"download": download_url, "width": 64, "height": 16},
                "thumb": {"download": download_url, "width": 128, "height": 33},
                "mini": {"download": download_url, "width": 200, "height": 52},
                "preview": {"download": download_url, "width": 215, "height": 56},
                "large": {"download": download_url, "width": 215, "height": 56},
            }
            self.assertEqual(
                {
                    "filename": "image.png",
                    "content-type": "image/png",
                    "size": 1185,
                    "download": download_url,
                    "width": 215,
                    "height": 56,
                    "scales": scales,
                },
                self.serialize(self.portal.image1)["image"],
            )

    def test_serialize_empty_image_returns_none(self):
        self.portal.invokeFactory("Image", id="image1", title="Image 1")
        self.assertEqual(None, self.serialize(self.portal.image1)["image"])

    def test_serialize_to_json_collection(self):
        self.portal.invokeFactory("Collection", id="collection1")
        self.portal.collection1.title = "My Collection"
        self.portal.collection1.description = "This is a collection with two documents"
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
            "Collection", self.serialize(self.portal.collection1).get("@type")
        )
        self.assertEqual(
            "Collection", self.serialize(self.portal.collection1).get("@type")
        )
        self.assertEqual(
            [
                {
                    "@id": self.portal.doc1.absolute_url(),
                    "@type": "Document",
                    "description": "",
                    "title": "Document 1",
                    "review_state": "private",
                },
                {
                    "@id": self.portal.doc2.absolute_url(),
                    "@type": "Document",
                    "description": "",
                    "title": "Document 2",
                    "review_state": "private",
                },
            ],
            self.serialize(self.portal.collection1).get("items"),
        )

    def test_serialize_to_json_collection_fullobjects(self):
        self.portal.invokeFactory("Collection", id="collection1")
        self.portal.collection1.title = "My Collection"
        self.portal.collection1.description = "This is a collection with two documents"
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
            "Collection", self.serialize(self.portal.collection1).get("@type")
        )
        self.assertEqual(
            "Collection", self.serialize(self.portal.collection1).get("@type")
        )

        items = self.serialize(self.portal.collection1, fullobjects=True).get("items")
        self.assertIn("UID", items[0])
        self.assertEqual(items[0]["id"], self.portal.doc1.getId())

        self.assertIn("UID", items[1])
        self.assertEqual(items[1]["id"], self.portal.doc2.getId())

    def test_serialize_to_json_collection_include_items(self):
        self.portal.invokeFactory("Collection", id="collection1")
        self.portal.collection1.title = "My Collection"
        self.portal.collection1.description = "This is a collection with two documents"
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
            "Collection", self.serialize(self.portal.collection1).get("@type")
        )
        self.assertEqual(
            "Collection", self.serialize(self.portal.collection1).get("@type")
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
