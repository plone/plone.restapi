from unittest.mock import patch
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.scale import storage
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import os
import transaction
import unittest


class TestTraversal(unittest.TestCase):

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

    def test_get_document(self):
        self.portal.invokeFactory("Document", id="doc1", title="My Document")
        self.portal.doc1.description = "This is a document"
        self.portal.doc1.text = RichTextValue("Lorem ipsum", "text/plain", "text/html")
        transaction.commit()

        response = self.api_session.get(self.portal.doc1.absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json",
            "When sending a GET request with Accept: application/json "
            + "the server should respond with sending back application/json: "
            + "{}".format(response.headers.get("Content-Type")),
        )
        self.assertEqual(
            "Document",
            response.json().get("@type"),
            "Response should be @type 'Document', not '{}'".format(
                response.json().get("@type")
            ),
        )
        self.assertEqual(
            response.json().get("@id"),
            self.portal.doc1.absolute_url(),
            "@id attribute != {}: {}".format(
                self.portal.doc1.absolute_url(), response.json()
            ),
        )
        self.assertEqual("My Document", response.json().get("title"))
        self.assertEqual("This is a document", response.json().get("description"))
        self.assertEqual(
            {
                "data": "<p>Lorem ipsum</p>",
                "content-type": "text/plain",
                "encoding": "utf-8",
            },
            response.json().get("text"),
        )

    def test_get_news_item(self):
        self.portal.invokeFactory("News Item", id="news1", title="News Item 1")
        image_file = os.path.join(os.path.dirname(__file__), "image.png")
        with open(image_file, "rb") as f:
            image_data = f.read()
        self.portal.news1.image = NamedBlobImage(
            data=image_data, contentType="image/png", filename="image.png"
        )
        self.portal.news1.image_caption = "This is an image caption."
        transaction.commit()

        with patch.object(storage, "uuid4", return_value="uuid1"):
            response = self.api_session.get(self.portal.news1.absolute_url())

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.headers.get("Content-Type"),
                "application/json",
                "When sending a GET request with Content-Type: application/json "
                + "the server should respond with sending back application/json.",  # noqa
            )
            self.assertEqual(
                "News Item",
                response.json().get("@type"),
                "Response should be @type 'News Item', not '{}'".format(
                    response.json().get("@type")
                ),
            )
            self.assertEqual(
                response.json().get("@id"), self.portal.news1.absolute_url()
            )
            self.assertEqual("News Item 1", response.json().get("title"))
            self.assertEqual(
                "This is an image caption.", response.json()["image_caption"]
            )
            self.assertDictContainsSubset(
                {"download": self.portal_url + "/news1/@@images/uuid1.png"},  # noqa
                response.json()["image"],
            )

    def test_get_folder(self):
        self.portal.invokeFactory("Folder", id="folder1", title="My Folder")
        transaction.commit()

        response = self.api_session.get(self.portal.folder1.absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json",
            "When sending a GET request with Content-Type: application/json "
            + "the server should respond with sending back application/json.",
        )
        self.assertEqual(
            "Folder",
            response.json().get("@type"),
            "Response should be @type 'Folder', not '{}'".format(
                response.json().get("@type")
            ),
        )
        self.assertEqual(self.portal.folder1.absolute_url(), response.json().get("@id"))
        self.assertEqual("My Folder", response.json().get("title"))

    def test_get_site_root(self):
        response = self.api_session.get(self.portal_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json",
            "When sending a GET request with Content-Type: application/json "
            + "the server should respond with sending back application/json.",
        )
        self.assertEqual(self.portal_url, response.json().get("@id"))
        self.assertEqual("Plone Site", response.json().get("@type"))

    def test_get_site_root_with_default_page(self):
        self.portal.invokeFactory("Document", id="front-page")
        self.portal.setDefaultPage("front-page")
        transaction.commit()

        response = self.api_session.get(self.portal_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json",
            "When sending a GET request with Content-Type: application/json "
            + "the server should respond with sending back application/json.",
        )
        self.assertEqual(response.json().get("@id"), self.portal_url)
        self.assertEqual("Plone Site", response.json().get("@type"))

    @unittest.skip("Not implemented yet.")
    def test_get_file(self):  # pragma: no cover
        self.portal.invokeFactory("File", id="file1")
        self.portal.file1.title = "File"
        self.portal.file1.description = "A file"
        pdf_file = os.path.join(os.path.dirname(__file__), "file.pdf")
        with open(pdf_file, "rb") as f:
            pdf_data = f.read()
        self.portal.file1.file = NamedBlobFile(
            data=pdf_data, contentType="application/pdf", filename="file.pdf"
        )
        intids = getUtility(IIntIds)
        file_id = intids.getId(self.portal.file1)
        self.portal.file1.file = RelationValue(file_id)
        transaction.commit()

        response = self.api_session.get(self.portal.file1.absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json",
            "When sending a GET request with Content-Type: application/json "
            + "the server should respond with sending back application/json.",
        )
        self.assertEqual(response.json()["@id"], self.portal.file1.absolute_url())

    @unittest.skip("Not implemented yet.")
    def test_get_image(self):  # pragma: no cover
        self.portal.invokeFactory("Image", id="img1")
        self.portal.img1.title = "Image"
        self.portal.img1.description = "An image"
        image_file = os.path.join(os.path.dirname(__file__), "image.png")
        with open(image_file, "rb") as f:
            image_data = f.read()
        self.portal.img1.image = NamedBlobImage(
            data=image_data, contentType="image/png", filename="image.png"
        )
        transaction.commit()

        response = self.api_session.get(self.portal.img1.absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json",
            "When sending a GET request with Content-Type: application/json "
            + "the server should respond with sending back application/json.",
        )
        self.assertEqual(response.json()["@id"], self.portal.img1.absolute_url())
