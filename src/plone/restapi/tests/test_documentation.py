# -*- coding: utf-8 -*-
from base64 import b64encode
from datetime import datetime
from mock import patch
from pkg_resources import parse_version
from pkg_resources import resource_filename
from plone import api
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import IReplies
from plone.app.testing import applyProfile
from plone.app.testing import popGlobalRegistry
from plone.app.testing import pushGlobalRegistry
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.locking.interfaces import ITTWLockable
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import PAM_INSTALLED  # noqa
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING
from plone.restapi.testing import register_static_uuid_utility
from plone.restapi.testing import RelativeSession
from plone.restapi.tests.statictime import StaticTime
from plone.scale import storage
from plone.testing.z2 import Browser
from six.moves import range
from zope.component import createObject
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.component.hooks import getSite

import collections
import json
import os
import re
import six
import transaction
import unittest


if PAM_INSTALLED:
    from plone.app.multilingual.interfaces import ITranslationManager


TUS_HEADERS = [
    "upload-offset",
    "upload-length",
    "upload-metadata",
    "tus-version",
    "tus-resumable",
    "tus-extension",
    "tus-max-size",
]

REQUEST_HEADER_KEYS = [
    "accept",
    "accept-language",
    "authorization",
    "lock-token",
    "prefer",
] + TUS_HEADERS

RESPONSE_HEADER_KEYS = ["content-type", "allow", "location"] + TUS_HEADERS


base_path = resource_filename("plone.restapi.tests", "http-examples")

UPLOAD_DATA = b"abcdefgh"
UPLOAD_MIMETYPE = b"text/plain"
UPLOAD_FILENAME = b"test.txt"
UPLOAD_LENGTH = len(UPLOAD_DATA)

UPLOAD_PDF_MIMETYPE = "application/pdf"
UPLOAD_PDF_FILENAME = "file.pdf"

PLONE_VERSION = parse_version(api.env.plone_version())

try:
    from Products.CMFPlone.factory import _IMREALLYPLONE5  # noqa
except ImportError:
    PLONE5 = False
else:
    PLONE5 = True


def pretty_json(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(",", ": "))


def save_request_and_response_for_docs(name, response):
    if six.PY2:
        open_kw = {}
    else:
        open_kw = {"newline": "\n"}
    filename = "{}/{}".format(base_path, "%s.req" % name)
    with open(filename, "w", **open_kw) as req:
        req.write(
            "{} {} HTTP/1.1\n".format(
                response.request.method, response.request.path_url
            )
        )
        ordered_request_headers = collections.OrderedDict(
            sorted(response.request.headers.items())
        )
        for key, value in ordered_request_headers.items():
            if key.lower() in REQUEST_HEADER_KEYS:
                req.write("{}: {}\n".format(key.title(), value))
        if response.request.body:
            # If request has a body, make sure to set Content-Type header
            if "content-type" not in REQUEST_HEADER_KEYS:
                content_type = response.request.headers["Content-Type"]
                req.write("Content-Type: %s\n" % content_type)

            req.write("\n")

            # Pretty print JSON request body
            if content_type == "application/json":
                json_body = json.loads(response.request.body)
                body = pretty_json(json_body)
                # Make sure Content-Length gets updated, just in case we
                # ever decide to dump that header
                response.request.prepare_body(data=body, files=None)

            req.flush()
            if isinstance(response.request.body, six.text_type) or not hasattr(
                req, "buffer"
            ):
                req.write(response.request.body)
            else:
                req.buffer.seek(0, 2)
                req.buffer.write(response.request.body)

    filename = "{}/{}".format(base_path, "%s.resp" % name)
    with open(filename, "w", **open_kw) as resp:
        status = response.status_code
        reason = response.reason
        resp.write("HTTP/1.1 {} {}\n".format(status, reason))
        for key, value in response.headers.items():
            if key.lower() in RESPONSE_HEADER_KEYS:
                resp.write("{}: {}\n".format(key.title(), value))
        resp.write("\n")
        resp.write(response.text)


def save_request_for_docs(name, response):
    if six.PY2:
        open_kw = {}
    else:
        open_kw = {"newline": "\n"}
    filename = "{}/{}".format(base_path, "%s.req" % name)
    with open(filename, "w", **open_kw) as req:
        req.write(
            "{} {} HTTP/1.1\n".format(
                response.request.method, response.request.path_url
            )
        )
        ordered_request_headers = collections.OrderedDict(
            sorted(response.request.headers.items())
        )
        for key, value in ordered_request_headers.items():
            if key.lower() in REQUEST_HEADER_KEYS:
                req.write("{}: {}\n".format(key.title(), value))
        if response.request.body:
            # If request has a body, make sure to set Content-Type header
            if "content-type" not in REQUEST_HEADER_KEYS:
                content_type = response.request.headers["Content-Type"]
                req.write("Content-Type: %s\n" % content_type)

            req.write("\n")

            # Pretty print JSON request body
            if content_type == "application/json":
                json_body = json.loads(response.request.body)
                body = pretty_json(json_body)
                # Make sure Content-Length gets updated, just in case we
                # ever decide to dump that header
                response.request.prepare_body(data=body, files=None)

            req.flush()
            if isinstance(response.request.body, six.text_type) or not hasattr(
                req, "buffer"
            ):
                req.write(response.request.body)
            else:
                req.buffer.seek(0, 2)
                req.buffer.write(response.request.body)


class TestDocumentationBase(unittest.TestCase):
    def setUp(self):
        self.statictime = self.setup_with_context_manager(StaticTime())

        self.app = self.layer["app"]
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        # Register custom UUID generator to produce stable UUIDs during tests
        pushGlobalRegistry(getSite())
        register_static_uuid_utility(prefix="SomeUUID")

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", "Basic %s:%s" % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        )

        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def setup_with_context_manager(self, cm):
        """Use a contextmanager to setUp a test case.

        Registering the cm's __exit__ as a cleanup hook *guarantees* that it
        will be called after a test run, unlike tearDown().

        This is used to make sure plone.restapi never leaves behind any time
        freezing monkey patches that haven't gotten reverted.
        """
        val = cm.__enter__()
        self.addCleanup(cm.__exit__, None, None, None)
        return val

    def tearDown(self):
        popGlobalRegistry(getSite())
        self.api_session.close()


class TestDocumentation(TestDocumentationBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestDocumentation, self).setUp()
        self.document = self.create_document()
        alsoProvides(self.document, ITTWLockable)

        transaction.commit()

    def tearDown(self):
        super(TestDocumentation, self).tearDown()

    def create_document(self):
        self.portal.invokeFactory("Document", id="front-page")
        document = self.portal["front-page"]
        document.title = u"Welcome to Plone"
        document.description = (
            u"Congratulations! You have successfully installed Plone."
        )
        document.text = RichTextValue(
            u"If you're seeing this instead of the web site you were "
            + u"expecting, the owner of this web site has just installed "
            + u"Plone. Do not contact the Plone Team or the Plone mailing "
            + u"lists about this.",
            "text/plain",
            "text/html",
        )
        return document

    def create_folder(self):
        self.portal.invokeFactory("Folder", id="folder")
        folder = self.portal["folder"]
        folder.title = "My Folder"
        folder.description = u"This is a folder with two documents"
        folder.invokeFactory("Document", id="doc1", title="A document within a folder")
        folder.invokeFactory("Document", id="doc2", title="A document within a folder")
        return folder

    def test_documentation_content_crud(self):
        folder = self.create_folder()
        transaction.commit()

        response = self.api_session.post(
            folder.absolute_url(), json={"@type": "Document", "title": "My Document"}
        )
        save_request_and_response_for_docs("content_post", response)

        transaction.commit()
        document = folder["my-document"]
        response = self.api_session.get(document.absolute_url())
        save_request_and_response_for_docs("content_get", response)

        response = self.api_session.get(
            folder.absolute_url() + "?metadata_fields=UID&metadata_fields=Creator"
        )
        save_request_and_response_for_docs("content_get_folder", response)

        response = self.api_session.patch(
            document.absolute_url(), json={"title": "My New Document Title"}
        )
        save_request_and_response_for_docs("content_patch", response)

        response = self.api_session.patch(
            document.absolute_url(),
            headers={"Prefer": "return=representation"},
            json={"title": "My New Document Title"},
        )
        save_request_and_response_for_docs("content_patch_representation", response)

        transaction.commit()
        response = self.api_session.delete(document.absolute_url())
        save_request_and_response_for_docs("content_delete", response)

    def test_documentation_document(self):
        response = self.api_session.get(self.document.absolute_url())
        save_request_and_response_for_docs("document", response)

    def test_documentation_news_item(self):
        self.portal.invokeFactory("News Item", id="newsitem")
        self.portal.newsitem.title = "My News Item"
        self.portal.newsitem.description = u"This is a news item"
        self.portal.newsitem.text = RichTextValue(
            u"Lorem ipsum", "text/plain", "text/html"
        )
        image_file = os.path.join(os.path.dirname(__file__), u"image.png")
        with open(image_file, "rb") as f:
            image_data = f.read()
        self.portal.newsitem.image = NamedBlobImage(
            data=image_data, contentType="image/png", filename=u"image.png"
        )
        self.portal.newsitem.image_caption = u"This is an image caption."
        transaction.commit()

        with patch.object(storage, "uuid4", return_value="uuid1"):
            response = self.api_session.get(self.portal.newsitem.absolute_url())
            save_request_and_response_for_docs("newsitem", response)

    def test_documentation_event(self):
        self.portal.invokeFactory("Event", id="event")
        self.portal.event.title = "Event"
        self.portal.event.description = u"This is an event"
        self.portal.event.start = datetime(2013, 1, 1, 10, 0)
        self.portal.event.end = datetime(2013, 1, 1, 12, 0)
        transaction.commit()
        response = self.api_session.get(self.portal.event.absolute_url())
        save_request_and_response_for_docs("event", response)

    def test_documentation_link(self):
        self.portal.invokeFactory("Link", id="link")
        self.portal.link.title = "My Link"
        self.portal.link.description = u"This is a link"
        self.portal.remoteUrl = "http://plone.org"
        transaction.commit()
        response = self.api_session.get(self.portal.link.absolute_url())
        save_request_and_response_for_docs("link", response)

    def test_documentation_file(self):
        self.portal.invokeFactory("File", id="file")
        self.portal.file.title = "My File"
        self.portal.file.description = u"This is a file"
        pdf_file = os.path.join(os.path.dirname(__file__), u"file.pdf")
        with open(pdf_file, "rb") as f:
            pdf_data = f.read()
        self.portal.file.file = NamedBlobFile(
            data=pdf_data, contentType="application/pdf", filename=u"file.pdf"
        )
        transaction.commit()
        response = self.api_session.get(self.portal.file.absolute_url())
        save_request_and_response_for_docs("file", response)

    def test_documentation_image(self):
        self.portal.invokeFactory("Image", id="image")
        self.portal.image.title = "My Image"
        self.portal.image.description = u"This is an image"
        image_file = os.path.join(os.path.dirname(__file__), u"image.png")
        with open(image_file, "rb") as f:
            image_data = f.read()
        self.portal.image.image = NamedBlobImage(
            data=image_data, contentType="image/png", filename=u"image.png"
        )
        transaction.commit()
        with patch.object(storage, "uuid4", return_value="uuid1"):
            response = self.api_session.get(self.portal.image.absolute_url())
            save_request_and_response_for_docs("image", response)

    def test_documentation_folder(self):
        folder = self.create_folder()
        transaction.commit()
        response = self.api_session.get(folder.absolute_url())
        save_request_and_response_for_docs("folder", response)

    def test_documentation_collection(self):
        self.portal.invokeFactory("Collection", id="collection")
        self.portal.collection.title = "My Collection"
        self.portal.collection.description = u"This is a collection with two documents"
        self.portal.collection.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.string.is",
                "v": "Document",
            }
        ]
        self.portal.invokeFactory("Document", id="doc1", title="Document 1")
        self.portal.invokeFactory("Document", id="doc2", title="Document 2")
        transaction.commit()
        response = self.api_session.get(self.portal.collection.absolute_url())
        save_request_and_response_for_docs("collection", response)

    def test_documentation_collection_fullobjects(self):
        self.portal.invokeFactory("Collection", id="collection")
        self.portal.collection.title = "My Collection"
        self.portal.collection.description = u"This is a collection with two documents"
        self.portal.collection.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.string.is",
                "v": "Document",
            }
        ]
        self.portal.invokeFactory("Document", id="doc1", title="Document 1")
        self.portal.invokeFactory("Document", id="doc2", title="Document 2")
        transaction.commit()
        response = self.api_session.get(
            self.portal.collection.absolute_url() + "?fullobjects"
        )
        save_request_and_response_for_docs("collection_fullobjects", response)

    def test_documentation_siteroot(self):
        response = self.api_session.get(self.portal.absolute_url())
        save_request_and_response_for_docs("siteroot", response)

    def test_documentation_404_not_found(self):
        response = self.api_session.get("non-existing-resource")
        save_request_and_response_for_docs("404_not_found", response)

    def test_documentation_search(self):
        query = {"sort_on": "path"}
        response = self.api_session.get("/@search", params=query)
        save_request_and_response_for_docs("search", response)

    def test_documentation_search_options(self):
        self.portal.invokeFactory("Folder", id="folder1", title="Folder 1")
        self.portal.folder1.invokeFactory("Folder", id="folder2", title="Folder 2")
        transaction.commit()
        query = {"sort_on": "path", "path.query": "/plone/folder1", "path.depth": "1"}
        response = self.api_session.get("/@search", params=query)
        save_request_and_response_for_docs("search_options", response)

    def test_documentation_search_multiple_paths(self):
        self.portal.invokeFactory("Folder", id="folder1", title="Folder 1")
        self.portal.folder1.invokeFactory("Document", id="doc1", title="Lorem Ipsum")
        self.portal.invokeFactory("Folder", id="folder2", title="Folder 2")
        self.portal.folder2.invokeFactory("Document", id="doc2", title="Lorem Ipsum")
        transaction.commit()
        query = {
            "sort_on": "path",
            "path.query": ["/plone/folder1", "/plone/folder2"],
            "path.depth": "2",
        }
        response = self.api_session.get("/@search", params=query)
        save_request_and_response_for_docs("search_multiple_paths", response)

    def test_documentation_search_metadata_fields(self):
        self.portal.invokeFactory("Document", id="doc1", title="Lorem Ipsum")
        transaction.commit()
        query = {"SearchableText": "lorem", "metadata_fields": ["modified", "created"]}
        response = self.api_session.get("/@search", params=query)
        save_request_and_response_for_docs("search_metadata_fields", response)

    def test_documentation_search_fullobjects(self):
        self.portal.invokeFactory("Document", id="doc1", title="Lorem Ipsum")
        transaction.commit()
        query = {"SearchableText": "lorem", "fullobjects": 1}
        response = self.api_session.get("/@search", params=query)
        save_request_and_response_for_docs("search_fullobjects", response)

    def test_documentation_workflow(self):
        response = self.api_session.get(
            "{}/@workflow".format(self.document.absolute_url())
        )
        save_request_and_response_for_docs("workflow_get", response)

    def test_documentation_workflow_transition(self):
        response = self.api_session.post(
            "{}/@workflow/publish".format(self.document.absolute_url())
        )
        save_request_and_response_for_docs("workflow_post", response)

    def test_documentation_workflow_transition_with_body(self):
        folder = self.portal[self.portal.invokeFactory("Folder", id="folder")]
        transaction.commit()
        response = self.api_session.post(
            "{}/@workflow/publish".format(folder.absolute_url()),
            json={
                "comment": "Publishing my folder...",
                "include_children": True,
                "effective": "2018-01-21T08:00:00",
                "expires": "2019-01-21T08:00:00",
            },
        )
        save_request_and_response_for_docs("workflow_post_with_body", response)

    def test_documentation_registry_get(self):
        response = self.api_session.get(
            "/@registry/plone.app.querystring.field.path.title"
        )
        save_request_and_response_for_docs("registry_get", response)

    def test_documentation_registry_update(self):
        response = self.api_session.patch(
            "/@registry/", json={"plone.app.querystring.field.path.title": "Value"}
        )
        save_request_and_response_for_docs("registry_update", response)

    def test_documentation_registry_get_list(self):
        response = self.api_session.get("/@registry")
        save_request_and_response_for_docs("registry_get_list", response)

    def test_documentation_types(self):
        response = self.api_session.get("/@types")
        save_request_and_response_for_docs("types", response)

    def test_documentation_types_document_crud(self):
        #
        # POST
        #

        # Add fieldset
        response = self.api_session.post(
            "/@types/Document",
            json={
                "factory": "fieldset",
                "title": "Contact Info",
                "description": "Contact information",
            },
        )
        save_request_and_response_for_docs("types_document_post_fieldset", response)

        # Add field
        response = self.api_session.post(
            "/@types/Document",
            json={
                "factory": "Email",
                "title": "Author email",
                "description": "Email of the author",
                "required": True,
            },
        )
        save_request_and_response_for_docs("types_document_post_field", response)

        #
        # GET
        #

        # Document
        response = self.api_session.get("/@types/Document")
        save_request_and_response_for_docs("types_document", response)
        doc_json = json.loads(response.content)

        # Get fieldset
        response = self.api_session.get("/@types/Document/contact_info")
        save_request_and_response_for_docs("types_document_get_fieldset", response)

        # Get field
        response = self.api_session.get("/@types/Document/author_email")
        save_request_and_response_for_docs("types_document_get_field", response)

        #
        # PATCH
        #

        # Update Document defaults
        response = self.api_session.patch(
            "/@types/Document",
            json={
                "properties": {
                    "author_email": {
                        "default": "foo@bar.com",
                        "minLength": 5,
                        "maxLength": 20,
                    }
                }
            },
        )
        save_request_and_response_for_docs("types_document_patch_properites", response)

        # Change field tab / order
        response = self.api_session.patch(
            "/@types/Document",
            json={
                "fieldsets": [
                    {
                        "id": "contact_info",
                        "title": "Contact info",
                        "fields": ["author_email"],
                    }
                ]
            },
        )
        save_request_and_response_for_docs("types_document_patch_fieldsets", response)

        # Update fieldset settings
        response = self.api_session.patch(
            "/@types/Document/contact_info",
            json={
                "title": "Contact information",
                "description": "Contact information",
                "fields": ["author_email"],
            },
        )
        save_request_and_response_for_docs("types_document_patch_fieldset", response)

        # Update field settings
        response = self.api_session.patch(
            "/@types/Document/author_email",
            json={
                "title": "Author e-mail",
                "description": "The e-mail address of the author",
                "minLength": 10,
                "maxLength": 20,
                "required": True,
            },
        )
        save_request_and_response_for_docs("types_document_patch_field", response)

        doc_json["layouts"] = ["thumbnail_view", "table_view"]
        doc_json["fieldsets"] = [
            {
                "id": "author",
                "title": "Contact the author",
                "fields": [
                    "author_email",
                    "author_url",
                    "author_name",
                ],
            },
            {"id": "contact_info", "title": "Contact info", "fields": []},
        ]

        doc_json["properties"]["author_name"] = {
            "description": "Name of the author",
            "factory": "Text line (String)",
            "title": "Author name",
        }

        doc_json["properties"]["author_url"] = {
            "description": "Author webpage",
            "factory": "URL",
            "title": "Author website",
            "minLength": 5,
            "maxLength": 30,
        }

        response = self.api_session.put("/@types/Document", json=doc_json)
        save_request_and_response_for_docs("types_document_put", response)

        #
        # DELETE
        #

        # Remove field
        response = self.api_session.delete(
            "/@types/Document/author_email",
        )
        save_request_and_response_for_docs("types_document_delete_field", response)

        # Remove fieldset
        response = self.api_session.delete(
            "/@types/Document/contact_info",
        )
        save_request_and_response_for_docs("types_document_delete_fieldset", response)

    def test_documentation_jwt_login(self):
        self.portal.acl_users.jwt_auth._secret = "secret"
        self.portal.acl_users.jwt_auth.use_keyring = False
        self.portal.acl_users.jwt_auth.token_timeout = 0
        transaction.commit()
        self.api_session.auth = None
        response = self.api_session.post(
            "{}/@login".format(self.portal.absolute_url()),
            json={"login": SITE_OWNER_NAME, "password": SITE_OWNER_PASSWORD},
        )
        save_request_and_response_for_docs("jwt_login", response)

    def test_documentation_jwt_logged_in(self):
        self.portal.acl_users.jwt_auth._secret = "secret"
        self.portal.acl_users.jwt_auth.use_keyring = False
        self.portal.acl_users.jwt_auth.token_timeout = 0
        self.portal.acl_users.jwt_auth.store_tokens = True
        transaction.commit()
        self.api_session.auth = None
        response = self.api_session.post(
            "{}/@login".format(self.portal.absolute_url()),
            json={"login": SITE_OWNER_NAME, "password": SITE_OWNER_PASSWORD},
        )
        token = json.loads(response.content)["token"]
        response = self.api_session.get(
            "/", headers={"Authorization": "Bearer {}".format(token)}
        )
        save_request_and_response_for_docs("jwt_logged_in", response)

    def test_documentation_jwt_login_renew(self):
        self.portal.acl_users.jwt_auth._secret = "secret"
        self.portal.acl_users.jwt_auth.use_keyring = False
        self.portal.acl_users.jwt_auth.token_timeout = 0
        transaction.commit()
        self.api_session.auth = None
        response = self.api_session.post(
            "{}/@login".format(self.portal.absolute_url()),
            json={"login": SITE_OWNER_NAME, "password": SITE_OWNER_PASSWORD},
        )
        token = json.loads(response.content)["token"]
        response = self.api_session.post(
            "{}/@login-renew".format(self.portal.absolute_url()),
            headers={"Authorization": "Bearer {}".format(token)},
        )
        save_request_and_response_for_docs("jwt_login_renew", response)

    def test_documentation_jwt_logout(self):
        self.portal.acl_users.jwt_auth._secret = "secret"
        self.portal.acl_users.jwt_auth.use_keyring = False
        self.portal.acl_users.jwt_auth.token_timeout = 0
        self.portal.acl_users.jwt_auth.store_tokens = True
        transaction.commit()
        self.api_session.auth = None
        response = self.api_session.post(
            "{}/@login".format(self.portal.absolute_url()),
            json={"login": SITE_OWNER_NAME, "password": SITE_OWNER_PASSWORD},
        )
        token = json.loads(response.content)["token"]
        response = self.api_session.post(
            "{}/@logout".format(self.portal.absolute_url()),
            headers={"Authorization": "Bearer {}".format(token)},
        )
        save_request_and_response_for_docs("jwt_logout", response)

    def test_documentation_batching(self):
        folder = self.portal[
            self.portal.invokeFactory("Folder", id="folder", title="Folder")
        ]
        for i in range(7):
            folder.invokeFactory(
                "Document", id="doc-%s" % str(i + 1), title="Document %s" % str(i + 1)
            )
        transaction.commit()

        query = {"sort_on": "path"}
        response = self.api_session.get("/folder/@search?b_size=5", params=query)
        save_request_and_response_for_docs("batching", response)

    def test_documentation_users(self):
        test_user = api.user.get(username=TEST_USER_ID)
        properties = {
            "description": "This is a test user",
            "email": "test@example.com",
            "fullname": "Test User",
            "home_page": "http://www.example.com",
            "location": "Bonn",
            "username": "test-user",
        }
        test_user.setMemberProperties(mapping=properties)
        admin = api.user.get(username="admin")
        properties = {
            "description": "This is an admin user",
            "email": "admin@example.com",
            "fullname": "Administrator",
            "home_page": "http://www.example.com",
            "location": "Berlin",
            "username": "admin",
        }
        admin.setMemberProperties(mapping=properties)
        transaction.commit()
        response = self.api_session.get("/@users")
        save_request_and_response_for_docs("users", response)

    def test_documentation_users_as_anonymous(self):
        logged_out_api_session = RelativeSession(self.portal_url)
        logged_out_api_session.headers.update({"Accept": "application/json"})

        response = logged_out_api_session.get("@users")
        save_request_and_response_for_docs("users_anonymous", response)
        self.assertEqual(response.status_code, 401)
        logged_out_api_session.close()

    def test_documentations_users_as_unauthorized_user(self):
        properties = {
            "email": "noam.chomsky@example.com",
            "username": "noamchomsky",
            "fullname": "Noam Avram Chomsky",
            "home_page": "web.mit.edu/chomsky",
            "description": "Professor of Linguistics",
            "location": "Cambridge, MA",
        }
        api.user.create(
            email="noam.chomsky@example.com",
            username="noam",
            password="password",
            properties=properties,
        )
        transaction.commit()

        standard_api_session = RelativeSession(self.portal_url)
        standard_api_session.headers.update({"Accept": "application/json"})
        standard_api_session.auth = ("noam", "password")

        response = standard_api_session.get("@users")
        save_request_and_response_for_docs("users_unauthorized", response)
        self.assertEqual(response.status_code, 401)
        standard_api_session.close()

    def test_documentation_users_get(self):
        properties = {
            "email": "noam.chomsky@example.com",
            "username": "noamchomsky",
            "fullname": "Noam Avram Chomsky",
            "home_page": "web.mit.edu/chomsky",
            "description": "Professor of Linguistics",
            "location": "Cambridge, MA",
        }
        api.user.create(
            email="noam.chomsky@example.com", username="noam", properties=properties
        )
        transaction.commit()
        response = self.api_session.get("@users/noam")
        save_request_and_response_for_docs("users_get", response)

    def test_documentation_users_anonymous_get(self):
        properties = {
            "email": "noam.chomsky@example.com",
            "username": "noamchomsky",
            "fullname": "Noam Avram Chomsky",
            "home_page": "web.mit.edu/chomsky",
            "description": "Professor of Linguistics",
            "location": "Cambridge, MA",
        }
        api.user.create(
            email="noam.chomsky@example.com", username="noam", properties=properties
        )
        transaction.commit()

        logged_out_api_session = RelativeSession(self.portal_url)
        logged_out_api_session.headers.update({"Accept": "application/json"})

        response = logged_out_api_session.get("@users/noam")
        save_request_and_response_for_docs("users_anonymous_get", response)
        logged_out_api_session.close()

    def test_documentation_users_unauthorized_get(self):
        properties = {
            "email": "noam.chomsky@example.com",
            "username": "noamchomsky",
            "fullname": "Noam Avram Chomsky",
            "home_page": "web.mit.edu/chomsky",
            "description": "Professor of Linguistics",
            "location": "Cambridge, MA",
        }
        api.user.create(
            email="noam.chomsky@example.com",
            username="noam",
            password="secret",
            properties=properties,
        )

        api.user.create(
            email="noam.chomsky@example.com",
            username="noam-fake",
            password="secret",
            properties=properties,
        )

        transaction.commit()

        logged_out_api_session = RelativeSession(self.portal_url)
        logged_out_api_session.headers.update({"Accept": "application/json"})
        logged_out_api_session.auth = ("noam-fake", "secret")

        response = logged_out_api_session.get("@users/noam")
        save_request_and_response_for_docs("users_unauthorized_get", response)
        logged_out_api_session.close()

    def test_documentation_users_authorized_get(self):
        properties = {
            "email": "noam.chomsky@example.com",
            "username": "noamchomsky",
            "fullname": "Noam Avram Chomsky",
            "home_page": "web.mit.edu/chomsky",
            "description": "Professor of Linguistics",
            "location": "Cambridge, MA",
        }
        api.user.create(
            email="noam.chomsky@example.com",
            username="noam",
            password="secret",
            properties=properties,
        )
        transaction.commit()

        logged_out_api_session = RelativeSession(self.portal_url)
        logged_out_api_session.headers.update({"Accept": "application/json"})
        logged_out_api_session.auth = ("noam", "secret")
        response = logged_out_api_session.get("@users/noam")
        save_request_and_response_for_docs("users_authorized_get", response)
        logged_out_api_session.close()

    def test_documentation_users_filtered_get(self):
        properties = {
            "email": "noam.chomsky@example.com",
            "username": "noamchomsky",
            "fullname": "Noam Avram Chomsky",
            "home_page": "web.mit.edu/chomsky",
            "description": "Professor of Linguistics",
            "location": "Cambridge, MA",
        }
        api.user.create(
            email="noam.chomsky@example.com", username="noam", properties=properties
        )
        transaction.commit()
        response = self.api_session.get("@users", params={"query": "noa"})
        save_request_and_response_for_docs(
            "users_filtered_by_username", response
        )  # noqa

    def test_documentation_users_created(self):
        response = self.api_session.post(
            "/@users",
            json={
                "email": "noam.chomsky@example.com",
                "password": "colorlessgreenideas",
                "username": "noamchomsky",
                "fullname": "Noam Avram Chomsky",
                "home_page": "web.mit.edu/chomsky",
                "description": "Professor of Linguistics",
                "location": "Cambridge, MA",
                "roles": ["Contributor"],
            },
        )
        save_request_and_response_for_docs("users_created", response)

    def test_documentation_users_add(self):
        response = self.api_session.post(
            "/@users",
            json={
                "email": "noam.chomsky@example.com",
                "username": "noamchomsky",
                "fullname": "Noam Avram Chomsky",
                "home_page": "web.mit.edu/chomsky",
                "description": "Professor of Linguistics",
                "location": "Cambridge, MA",
                "sendPasswordReset": True,
            },
        )
        save_request_and_response_for_docs("users_add", response)

    def test_documentation_users_update(self):
        properties = {
            "email": "noam.chomsky@example.com",
            "username": "noamchomsky",
            "fullname": "Noam Avram Chomsky",
            "home_page": "web.mit.edu/chomsky",
            "description": "Professor of Linguistics",
            "location": "Cambridge, MA",
        }
        api.user.create(
            email="noam.chomsky@example.com", username="noam", properties=properties
        )
        transaction.commit()

        response = self.api_session.patch(
            "/@users/noam",
            json={
                "email": "avram.chomsky@example.com",
                "roles": {"Contributor": False},
            },
        )
        save_request_and_response_for_docs("users_update", response)

    def test_documentation_users_update_portrait(self):
        payload = {
            "portrait": {
                "filename": "image.gif",
                "encoding": "base64",
                "data": "R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=",
                "content-type": "image/gif",
            }
        }
        api.user.create(email="noam.chomsky@example.com", username="noam")
        transaction.commit()
        response = self.api_session.patch("/@users/noam", json=payload)
        transaction.commit()

        response_get = self.api_session.get("/@users/noam", json=payload)

        save_request_and_response_for_docs("users_update_portrait", response)
        save_request_and_response_for_docs("users_update_portrait_get", response_get)

    def test_documentation_users_update_portrait_with_scale(self):
        payload = {
            "portrait": {
                "filename": "image.gif",
                "encoding": "base64",
                "data": "R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=",
                "content-type": "image/gif",
                "scale": True,
            }
        }
        api.user.create(email="noam.chomsky@example.com", username="noam")
        transaction.commit()
        response = self.api_session.patch("/@users/noam", json=payload)

        save_request_and_response_for_docs("users_update_portrait_scale", response)

    def test_documentation_users_delete(self):
        properties = {
            "email": "noam.chomsky@example.com",
            "username": "noamchomsky",
            "fullname": "Noam Avram Chomsky",
            "home_page": "web.mit.edu/chomsky",
            "description": "Professor of Linguistics",
            "location": "Cambridge, MA",
        }
        api.user.create(
            email="noam.chomsky@example.com", username="noam", properties=properties
        )
        transaction.commit()

        response = self.api_session.delete("/@users/noam")
        save_request_and_response_for_docs("users_delete", response)

    def test_documentation_groups(self):
        gtool = api.portal.get_tool("portal_groups")
        properties = {
            "title": "Plone Team",
            "description": "We are Plone",
            "email": "ploneteam@plone.org",
        }
        gtool.addGroup(
            "ploneteam",
            (),
            (),
            properties=properties,
            title=properties["title"],
            description=properties["description"],
        )
        transaction.commit()
        response = self.api_session.get("/@groups")
        save_request_and_response_for_docs("groups", response)

    def test_documentation_groups_get(self):
        gtool = api.portal.get_tool("portal_groups")
        properties = {
            "title": "Plone Team",
            "description": "We are Plone",
            "email": "ploneteam@plone.org",
        }
        gtool.addGroup(
            "ploneteam",
            (),
            (),
            properties=properties,
            title=properties["title"],
            description=properties["description"],
        )
        transaction.commit()
        response = self.api_session.get("@groups/ploneteam")
        save_request_and_response_for_docs("groups_get", response)

    def test_documentation_groups_filtered_get(self):
        gtool = api.portal.get_tool("portal_groups")
        properties = {
            "title": "Plone Team",
            "description": "We are Plone",
            "email": "ploneteam@plone.org",
        }
        gtool.addGroup(
            "ploneteam",
            (),
            (),
            properties=properties,
            title=properties["title"],
            description=properties["description"],
        )
        transaction.commit()
        response = self.api_session.get("@groups", params={"query": "plo"})
        save_request_and_response_for_docs(
            "groups_filtered_by_groupname", response
        )  # noqa

    def test_documentation_groups_created(self):
        response = self.api_session.post(
            "/@groups",
            json={
                "groupname": "fwt",
                "email": "fwt@plone.org",
                "title": "Framework Team",
                "description": "The Plone Framework Team",
                "roles": ["Manager"],
                "groups": ["Administrators"],
                "users": [SITE_OWNER_NAME, TEST_USER_ID],
            },
        )
        save_request_and_response_for_docs("groups_created", response)

    def test_documentation_groups_update(self):
        gtool = api.portal.get_tool("portal_groups")
        properties = {
            "title": "Plone Team",
            "description": "We are Plone",
            "email": "ploneteam@plone.org",
        }
        gtool.addGroup(
            "ploneteam",
            (),
            (),
            properties=properties,
            title=properties["title"],
            description=properties["description"],
        )
        transaction.commit()

        response = self.api_session.patch(
            "/@groups/ploneteam",
            json={"email": "ploneteam2@plone.org", "users": {TEST_USER_ID: False}},
        )
        save_request_and_response_for_docs("groups_update", response)

    def test_documentation_groups_delete(self):
        gtool = api.portal.get_tool("portal_groups")
        properties = {
            "title": "Plone Team",
            "description": "We are Plone",
            "email": "ploneteam@plone.org",
        }
        gtool.addGroup(
            "ploneteam",
            (),
            (),
            properties=properties,
            title=properties["title"],
            description=properties["description"],
        )
        transaction.commit()

        response = self.api_session.delete("/@groups/ploneteam")
        save_request_and_response_for_docs("groups_delete", response)

    def test_documentation_breadcrumbs(self):
        response = self.api_session.get(
            "{}/@breadcrumbs".format(self.document.absolute_url())
        )
        save_request_and_response_for_docs("breadcrumbs", response)

    def test_documentation_navigation(self):
        response = self.api_session.get(
            "{}/@navigation".format(self.document.absolute_url())
        )
        save_request_and_response_for_docs("navigation", response)

    def test_documentation_navigation_tree(self):
        folder = createContentInContainer(
            self.portal, u"Folder", id=u"folder", title=u"Some Folder"
        )
        createContentInContainer(
            self.portal, u"Folder", id=u"folder2", title=u"Some Folder 2"
        )
        subfolder1 = createContentInContainer(
            folder, u"Folder", id=u"subfolder1", title=u"SubFolder 1"
        )
        createContentInContainer(
            folder, u"Folder", id=u"subfolder2", title=u"SubFolder 2"
        )
        thirdlevelfolder = createContentInContainer(
            subfolder1, u"Folder", id=u"thirdlevelfolder", title=u"Third Level Folder"
        )
        createContentInContainer(
            thirdlevelfolder,
            u"Folder",
            id=u"fourthlevelfolder",
            title=u"Fourth Level Folder",
        )
        createContentInContainer(folder, u"Document", id=u"doc1", title=u"A document")
        transaction.commit()

        response = self.api_session.get(
            "{}/@navigation".format(self.document.absolute_url()),
            params={"expand.navigation.depth": 4},
        )
        save_request_and_response_for_docs("navigation_tree", response)

    def test_documentation_principals(self):
        gtool = api.portal.get_tool("portal_groups")
        properties = {
            "title": "Plone Team",
            "description": "We are Plone",
            "email": "ploneteam@plone.org",
        }
        gtool.addGroup(
            "ploneteam",
            (),
            (),
            properties=properties,
            title=properties["title"],
            description=properties["description"],
        )
        transaction.commit()
        response = self.api_session.get("/@principals", params={"search": "ploneteam"})
        save_request_and_response_for_docs("principals", response)

    def test_documentation_copy(self):
        response = self.api_session.post(
            "/@copy", json={"source": self.document.absolute_url()}
        )
        save_request_and_response_for_docs("copy", response)

    def test_documentation_copy_multiple(self):
        newsitem = self.portal[self.portal.invokeFactory("News Item", id="newsitem")]
        newsitem.title = "My News Item"
        transaction.commit()

        response = self.api_session.post(
            "/@copy",
            json={"source": [self.document.absolute_url(), newsitem.absolute_url()]},
        )
        save_request_and_response_for_docs("copy_multiple", response)

    def test_documentation_move(self):
        self.portal.invokeFactory("Folder", id="folder")
        transaction.commit()
        response = self.api_session.post(
            "/folder/@move", json={"source": self.document.absolute_url()}
        )
        save_request_and_response_for_docs("move", response)

    def test_documentation_vocabularies_all(self):
        response = self.api_session.get("/@vocabularies")
        save_request_and_response_for_docs("vocabularies", response)

    def test_documentation_vocabularies_get(self):
        response = self.api_session.get(
            "/@vocabularies/plone.app.vocabularies.ReallyUserFriendlyTypes"
        )
        save_request_and_response_for_docs("vocabularies_get", response)

    def test_documentation_vocabularies_get_fields(self):
        response = self.api_session.get("/@vocabularies/Fields")
        save_request_and_response_for_docs("vocabularies_get_fields", response)

    def test_documentation_vocabularies_get_filtered_by_title(self):
        response = self.api_session.get(
            "/@vocabularies/plone.app.vocabularies.ReallyUserFriendlyTypes?" "title=doc"
        )
        save_request_and_response_for_docs(
            "vocabularies_get_filtered_by_title", response
        )

    def test_documentation_vocabularies_get_filtered_by_token(self):
        response = self.api_session.get(
            "/@vocabularies/plone.app.vocabularies.ReallyUserFriendlyTypes?"
            "token=Document"
        )
        save_request_and_response_for_docs(
            "vocabularies_get_filtered_by_token", response
        )

    def test_documentation_sources_get(self):
        api.content.create(
            container=self.portal, id="doc", type="DXTestDocument", title=u"DX Document"
        )
        transaction.commit()
        response = self.api_session.get("/doc/@sources/test_choice_with_source")
        save_request_and_response_for_docs("sources_get", response)

    def test_documentation_sharing_folder_get(self):
        self.portal.invokeFactory("Folder", id="folder")
        transaction.commit()
        response = self.api_session.get("/folder/@sharing")
        save_request_and_response_for_docs("sharing_folder_get", response)

    def test_documentation_sharing_folder_post(self):
        self.portal.invokeFactory("Folder", id="folder")
        transaction.commit()
        payload = {
            "inherit": True,
            "entries": [
                {
                    "id": "AuthenticatedUsers",
                    "roles": {
                        "Reviewer": True,
                        "Editor": False,
                        "Reader": True,
                        "Contributor": False,
                    },
                    "type": "user",
                }
            ],
        }
        response = self.api_session.post("/folder/@sharing", json=payload)
        save_request_and_response_for_docs("sharing_folder_post", response)

    def test_documentation_sharing_search(self):
        self.portal.invokeFactory("Folder", id="folder")
        self.portal.folder.invokeFactory("Document", id="doc")
        api.user.grant_roles("admin", roles=["Contributor"])
        api.user.grant_roles("admin", roles=["Editor"], obj=self.portal.folder)
        transaction.commit()
        response = self.api_session.get("/folder/doc/@sharing?search=admin")
        save_request_and_response_for_docs("sharing_search", response)

    def test_documentation_expansion(self):
        response = self.api_session.get("/front-page")
        save_request_and_response_for_docs("expansion", response)

    def test_documentation_expansion_expanded(self):
        response = self.api_session.get("/front-page?expand=breadcrumbs")
        save_request_and_response_for_docs("expansion_expanded", response)

    def test_documentation_expansion_expanded_full(self):
        response = self.api_session.get(
            "/front-page?expand=actions,breadcrumbs,navigation,workflow,types"
        )
        save_request_and_response_for_docs("expansion_expanded_full", response)

    def test_history_get(self):
        self.document.setTitle("My new title")
        url = "{}/@history".format(self.document.absolute_url())
        response = self.api_session.get(url)
        save_request_and_response_for_docs("history_get", response)

    def test_history_revert(self):
        url = "{}/@history".format(self.document.absolute_url())
        response = self.api_session.patch(url, json={"version": 0})
        save_request_and_response_for_docs("history_revert", response)

    def test_tusupload_options(self):
        self.portal.invokeFactory("Folder", id="folder")
        transaction.commit()
        response = self.api_session.options("/folder/@tus-upload")
        save_request_and_response_for_docs("tusupload_options", response)

    def test_tusupload_post_head_patch(self):
        # We create both the POST and PATCH example here, because we need the
        # temporary id

        def clean_upload_url(response, _id="032803b64ad746b3ab46d9223ea3d90f"):
            pattern = r"@tus-upload/(\w+)"
            repl = "@tus-upload/" + _id

            # Replaces the dynamic part in the headers with a stable id
            for target in [response, response.request]:
                for key, val in target.headers.items():
                    target.headers[key] = re.sub(pattern, repl, val)

                target.url = re.sub(pattern, repl, target.url)

        def clean_final_url(response, _id="document-2016-10-21"):
            url = self.portal.folder.absolute_url() + "/" + _id
            response.headers["Location"] = url

        self.portal.invokeFactory("Folder", id="folder")
        transaction.commit()

        # POST create an upload
        metadata = "filename {},content-type {}".format(
            b64encode(UPLOAD_FILENAME).decode("utf-8"),
            b64encode(UPLOAD_MIMETYPE).decode("utf-8"),
        )
        response = self.api_session.post(
            "/folder/@tus-upload",
            headers={
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(UPLOAD_LENGTH),
                "Upload-Metadata": metadata,
            },
        )

        upload_url = response.headers["location"]

        clean_upload_url(response)
        save_request_and_response_for_docs("tusupload_post", response)

        # PATCH upload a partial document
        response = self.api_session.patch(
            upload_url,
            headers={
                "Tus-Resumable": "1.0.0",
                "Content-Type": "application/offset+octet-stream",
                "Upload-Offset": "0",
            },
            data=UPLOAD_DATA[:3],
        )
        clean_upload_url(response)
        save_request_and_response_for_docs("tusupload_patch", response)

        # HEAD ask for much the server has
        response = self.api_session.head(upload_url, headers={"Tus-Resumable": "1.0.0"})
        clean_upload_url(response)
        save_request_and_response_for_docs("tusupload_head", response)

        # Finalize the upload
        response = self.api_session.patch(
            upload_url,
            headers={
                "Tus-Resumable": "1.0.0",
                "Content-Type": "application/offset+octet-stream",
                "Upload-Offset": response.headers["Upload-Offset"],
            },
            data=UPLOAD_DATA[3:],
        )
        clean_upload_url(response)
        clean_final_url(response)
        save_request_and_response_for_docs("tusupload_patch_finalized", response)

    def test_tusreplace_post_patch(self):
        self.portal.invokeFactory("File", id="myfile")
        transaction.commit()

        # POST create an upload
        metadata = "filename {},content-type {}".format(
            b64encode(UPLOAD_FILENAME).decode("utf-8"),
            b64encode(UPLOAD_MIMETYPE).decode("utf-8"),
        )
        response = self.api_session.post(
            "/myfile/@tus-replace",
            headers={
                "Tus-Resumable": "1.0.0",
                "Upload-Length": str(UPLOAD_LENGTH),
                "Upload-Metadata": metadata,
            },
        )
        upload_url = response.headers["location"]
        # Replace dynamic uuid with a static one
        response.headers["location"] = "/".join(
            upload_url.split("/")[:-1] + ["4e465958b24a46ec8657e6f3be720991"]
        )
        save_request_and_response_for_docs("tusreplace_post", response)

        # PATCH upload file data
        response = self.api_session.patch(
            upload_url,
            headers={
                "Tus-Resumable": "1.0.0",
                "Content-Type": "application/offset+octet-stream",
                "Upload-Offset": "0",
            },
            data=UPLOAD_DATA,
        )
        # Replace dynamic uuid with a static one
        response.request.url = "/".join(
            upload_url.split("/")[:-1] + ["4e465958b24a46ec8657e6f3be720991"]
        )
        save_request_and_response_for_docs("tusreplace_patch", response)

    def test_locking_lock(self):
        url = "{}/@lock".format(self.document.absolute_url())
        response = self.api_session.post(url)
        # Replace dynamic lock token with a static one
        response._content = re.sub(
            b'"token": "[^"]+"',
            b'"token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"',  # noqa
            response.content,
        )
        save_request_and_response_for_docs("lock", response)

    def test_locking_lock_nonstealable_and_timeout(self):
        url = "{}/@lock".format(self.document.absolute_url())
        response = self.api_session.post(
            url, json={"stealable": False, "timeout": 3600}
        )
        # Replace dynamic lock token with a static one
        response._content = re.sub(
            b'"token": "[^"]+"',
            b'"token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"',  # noqa
            response.content,
        )
        save_request_and_response_for_docs("lock_nonstealable_timeout", response)

    def test_locking_unlock(self):
        url = "{}/@lock".format(self.document.absolute_url())
        response = self.api_session.post(url)
        url = "{}/@unlock".format(self.document.absolute_url())
        response = self.api_session.post(url)
        save_request_and_response_for_docs("unlock", response)

    def test_locking_refresh_lock(self):
        url = "{}/@lock".format(self.document.absolute_url())
        response = self.api_session.post(url)
        url = "{}/@refresh-lock".format(self.document.absolute_url())
        response = self.api_session.post(url)
        # Replace dynamic lock token with a static one
        response._content = re.sub(
            b'"token": "[^"]+"',
            b'"token": "0.684672730996-0.25195226375-00105A989226:1477076400.000"',  # noqa
            response.content,
        )
        save_request_and_response_for_docs("refresh_lock", response)

    def test_locking_lockinfo(self):
        url = "{}/@lock".format(self.document.absolute_url())
        response = self.api_session.get(url)
        save_request_and_response_for_docs("lock_get", response)

    def test_update_with_lock(self):
        url = "{}/@lock".format(self.document.absolute_url())
        response = self.api_session.post(url)
        token = response.json()["token"]
        response = self.api_session.patch(
            self.document.absolute_url(),
            headers={"Lock-Token": token},
            json={"title": "New Title"},
        )
        response.request.headers[
            "Lock-Token"
        ] = u"0.684672730996-0.25195226375-00105A989226:1477076400.000"  # noqa
        save_request_and_response_for_docs("lock_update", response)

    def test_querystring_get(self):
        url = "/@querystring"
        response = self.api_session.get(url)
        save_request_and_response_for_docs("querystring_get", response)

    def test_querystringsearch_post(self):
        url = "/@querystring-search"

        self.portal.invokeFactory("Document", "testdocument", title="Test Document")
        transaction.commit()

        response = self.api_session.post(
            url,
            json={
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": ["Document"],
                    }
                ]
            },
        )
        save_request_and_response_for_docs("querystringsearch_post", response)

    def test_system_get(self):
        response = self.api_session.get("/@system")
        save_request_for_docs("system_get", response)

    def test_database_get(self):
        response = self.api_session.get("/@database")
        save_request_for_docs("database_get", response)


class TestDocumentationMessageTranslations(TestDocumentationBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestDocumentationMessageTranslations, self).setUp()

        self.api_session.headers.update({"Accept-Language": "es"})

        self.document = self.create_document()
        alsoProvides(self.document, ITTWLockable)
        transaction.commit()

    def tearDown(self):
        super(TestDocumentationMessageTranslations, self).tearDown()

    def create_document(self):
        self.portal.invokeFactory("Document", id="front-page")
        document = self.portal["front-page"]
        document.title = u"Welcome to Plone"
        document.description = (
            u"Congratulations! You have successfully installed Plone."
        )
        document.text = RichTextValue(
            u"If you're seeing this instead of the web site you were "
            + u"expecting, the owner of this web site has just installed "
            + u"Plone. Do not contact the Plone Team or the Plone mailing "
            + u"lists about this.",
            "text/plain",
            "text/html",
        )
        return document

    def test_translate_messages_types(self):
        response = self.api_session.get("/@types")
        save_request_and_response_for_docs("translated_messages_types", response)

    def test_translate_messages_types_folder(self):
        response = self.api_session.get("/@types/Folder")
        save_request_and_response_for_docs("translated_messages_types_folder", response)

    def test_translate_messages_object_workflow(self):
        response = self.api_session.get("{}/@workflow".format(self.document.id))
        save_request_and_response_for_docs(
            "translated_messages_object_workflow", response
        )

    def test_translate_messages_object_history(self):
        response = self.api_session.get("{}/@history".format(self.document.id))
        save_request_and_response_for_docs(
            "translated_messages_object_history", response
        )


class TestCommenting(TestDocumentationBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestCommenting, self).setUp()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        settings.edit_comment_enabled = True
        settings.delete_own_comment_enabled = True

        self.document = self.create_document_with_comments()
        transaction.commit()

    def tearDown(self):
        super(TestCommenting, self).tearDown()

    def create_document_with_comments(self):
        self.portal.invokeFactory("Document", id="front-page")
        document = self.portal["front-page"]
        document.allow_discussion = True
        document.title = u"Welcome to Plone"
        document.description = (
            u"Congratulations! You have successfully installed Plone."
        )
        document.text = RichTextValue(
            u"If you're seeing this instead of the web site you were "
            + u"expecting, the owner of this web site has just installed "
            + u"Plone. Do not contact the Plone Team or the Plone mailing "
            + u"lists about this.",
            "text/plain",
            "text/html",
        )

        # Add a bunch of comments to the default conversation so we can do
        # batching
        self.conversation = conversation = IConversation(document)
        self.replies = replies = IReplies(conversation)
        for x in range(1, 2):
            comment = createObject("plone.Comment")
            comment.text = "Comment %d" % x
            comment = replies[replies.addComment(comment)]

            comment_replies = IReplies(comment)
            for y in range(1, 2):
                comment = createObject("plone.Comment")
                comment.text = "Comment %d.%d" % (x, y)
                comment_replies.addComment(comment)
        self.comment_id, self.comment = list(replies.items())[0]

        return document

    @staticmethod
    def clean_comment_id_from_urls(response, _id="123456"):
        pattern = r"@comments/(\w+)"
        pattern_bytes = b"@comments/(\\w+)"
        repl = "@comments/" + _id

        # Replaces the dynamic part in the headers with a stable id
        for target in [response, response.request]:
            for key, val in target.headers.items():
                target.headers[key] = re.sub(pattern, repl, val)

            target.url = re.sub(pattern, repl, target.url)

        # and the body
        if response.request.body:
            response.request.body = re.sub(pattern_bytes, repl, response.request.body)

        # and the response
        if response.content:
            response._content = re.sub(
                pattern_bytes, repl.encode("utf-8"), response._content
            )

    @staticmethod
    def clean_comment_id_from_body(response):
        # Build a mapping of all comment IDs found in the response, and
        # replace them with static ones.
        # Assumption: comment IDs are long enough to be unique.
        pattern_bytes = re.compile(b'"comment_id": "(\\w+)"')
        comment_ids = re.findall(pattern_bytes, response._content)

        def new_cid(idx):
            return str(idx + 1400000000000000).encode("ascii")

        static_comment_ids = {
            old_cid: new_cid(idx) for idx, old_cid in enumerate(comment_ids)
        }

        for cid, idx in static_comment_ids.items():
            response._content = re.sub(cid, idx, response._content)

    def test_comments_get(self):
        url = "{}/@comments".format(self.document.absolute_url())
        response = self.api_session.get(url)
        self.clean_comment_id_from_body(response)
        save_request_and_response_for_docs("comments_get", response)

    def test_comments_add_root(self):
        url = "{}/@comments/".format(self.document.absolute_url())
        payload = {"text": "My comment"}
        response = self.api_session.post(url, json=payload)
        self.clean_comment_id_from_urls(response)
        save_request_and_response_for_docs("comments_add_root", response)

    def test_comments_add_sub(self):
        # Add a reply
        url = "{}/@comments/{}".format(self.document.absolute_url(), self.comment_id)
        payload = {"text": "My reply"}
        response = self.api_session.post(url, json=payload)

        self.clean_comment_id_from_urls(response)
        save_request_and_response_for_docs("comments_add_sub", response)

    def test_comments_update(self):
        url = "{}/@comments/{}".format(self.document.absolute_url(), self.comment_id)
        payload = {"text": "My NEW comment"}
        response = self.api_session.patch(url, json=payload)
        self.clean_comment_id_from_urls(response)
        save_request_and_response_for_docs("comments_update", response)

    def test_comments_delete(self):
        url = "{}/@comments/{}".format(self.document.absolute_url(), self.comment_id)
        response = self.api_session.delete(url)
        self.clean_comment_id_from_urls(response)
        save_request_and_response_for_docs("comments_delete", response)

    def test_roles_get(self):
        url = "{}/@roles".format(self.portal_url)
        response = self.api_session.get(url)
        save_request_and_response_for_docs("roles", response)

    def test_documentation_expansion(self):
        response = self.api_session.get("/front-page?expand=breadcrumbs,workflow")
        save_request_and_response_for_docs("expansion", response)


@unittest.skipIf(not PLONE5, "Just Plone 5 currently.")
class TestControlPanelDocumentation(TestDocumentationBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def test_controlpanels_get_listing(self):
        response = self.api_session.get("/@controlpanels")
        save_request_and_response_for_docs("controlpanels_get", response)

    def test_controlpanels_get_item(self):
        response = self.api_session.get("/@controlpanels/editing")
        save_request_and_response_for_docs("controlpanels_get_item", response)

    def test_controlpanels_get_dexterity(self):
        response = self.api_session.get("/@controlpanels/dexterity-types")
        save_request_and_response_for_docs("controlpanels_get_dexterity", response)

    def test_controlpanels_crud_dexterity(self):
        # POST
        response = self.api_session.post(
            "/@controlpanels/dexterity-types",
            json={
                "title": "My Custom Content Type",
                "description": "A custom content-type",
            },
        )
        save_request_and_response_for_docs(
            "controlpanels_post_dexterity_item", response
        )

        # GET
        response = self.api_session.get(
            "/@controlpanels/dexterity-types/my_custom_content_type"
        )
        save_request_and_response_for_docs("controlpanels_get_dexterity_item", response)

        # PATCH
        response = self.api_session.patch(
            "/@controlpanels/dexterity-types/my_custom_content_type",
            json={
                "title": "My Content Type",
                "description": "A content-type",
                "plone.richtext": True,
                "plone.versioning": True,
            },
        )
        save_request_and_response_for_docs(
            "controlpanels_patch_dexterity_item", response
        )

        # DELETE
        response = self.api_session.delete(
            "/@controlpanels/dexterity-types/my_custom_content_type"
        )
        save_request_and_response_for_docs(
            "controlpanels_delete_dexterity_item", response
        )


@unittest.skipUnless(
    PAM_INSTALLED, "plone.app.multilingual is installed by default only in Plone 5"
)  # NOQA
class TestPAMDocumentation(TestDocumentationBase):

    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestPAMDocumentation, self).setUp()

        language_tool = api.portal.get_tool("portal_languages")
        language_tool.addSupportedLanguage("en")
        language_tool.addSupportedLanguage("es")
        language_tool.addSupportedLanguage("de")
        applyProfile(self.portal, "plone.app.multilingual:default")

        en_id = self.portal["en"].invokeFactory(
            "Document", id="test-document", title="Test document"
        )
        self.en_content = self.portal["en"].get(en_id)
        es_id = self.portal["es"].invokeFactory(
            "Document", id="test-document", title="Test document"
        )
        self.es_content = self.portal["es"].get(es_id)
        transaction.commit()

    def tearDown(self):
        super(TestPAMDocumentation, self).tearDown()

    def test_documentation_translations_post(self):
        response = self.api_session.post(
            "{}/@translations".format(self.en_content.absolute_url()),
            json={"id": self.es_content.absolute_url()},
        )
        save_request_and_response_for_docs("translations_post", response)

    def test_documentation_translations_post_by_id(self):
        response = self.api_session.post(
            "{}/@translations".format(self.en_content.absolute_url()),
            json={"id": self.es_content.absolute_url().replace(self.portal_url, "")},
        )
        save_request_and_response_for_docs("translations_post_by_id", response)

    def test_documentation_translations_post_by_uid(self):
        response = self.api_session.post(
            "{}/@translations".format(self.en_content.absolute_url()),
            json={"id": self.es_content.UID()},
        )
        save_request_and_response_for_docs("translations_post_by_uid", response)

    def test_documentation_translations_get(self):
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        transaction.commit()
        response = self.api_session.get(
            "{}/@translations".format(self.en_content.absolute_url())
        )

        save_request_and_response_for_docs("translations_get", response)

    def test_documentation_translations_delete(self):
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        transaction.commit()
        response = self.api_session.delete(
            "{}/@translations".format(self.en_content.absolute_url()),
            json={"language": "es"},
        )
        save_request_and_response_for_docs("translations_delete", response)

    def test_documentation_translations_link_on_post(self):
        response = self.api_session.post(
            "{}/de".format(self.portal.absolute_url()),
            json={
                "@type": "Document",
                "id": "mydocument",
                "title": "My German Document",
                "translation_of": self.es_content.UID(),
                "language": "de",
            },
        )
        save_request_and_response_for_docs("translations_link_on_post", response)

    def test_documentation_translation_locator(self):
        response = self.api_session.get(
            "{}/@translation-locator?target_language=de".format(
                self.es_content.absolute_url()
            ),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        save_request_and_response_for_docs("translation_locator", response)
