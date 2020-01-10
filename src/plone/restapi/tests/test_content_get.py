# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
from plone.restapi.testing import HAS_AT
from plone.restapi.testing import HAS_DX
from plone.restapi.testing import PLONE_RESTAPI_AT_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from Products.CMFCore.utils import getToolByName
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import os
import requests
import transaction
import unittest


class TestContentGet(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        if not HAS_DX:
            raise unittest.SkipTest("Skip tests if Dexterity is not present")
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory("Folder", id="folder1", title="My Folder")
        self.portal.folder1.invokeFactory("Document", id="doc1", title="My Document")
        self.portal.folder1.doc1.text = RichTextValue(
            u"Lorem ipsum.", "text/plain", "text/html"
        )
        self.portal.folder1.invokeFactory("Folder", id="folder2", title="My Folder 2")
        self.portal.folder1.folder2.invokeFactory(
            "Document", id="doc2", title="My Document 2"
        )
        self.portal.folder1.invokeFactory(
            "Collection", id="collection", title="My collection"
        )
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(self.portal.folder1, "publish")
        wftool.doActionFor(self.portal.folder1.doc1, "publish")
        wftool.doActionFor(self.portal.folder1.folder2, "publish")
        wftool.doActionFor(self.portal.folder1.folder2.doc2, "publish")
        transaction.commit()

    def test_get_content_returns_fullobjects(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + "?fullobjects",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(3, len(response.json()["items"]))
        self.assertTrue("title" in list(response.json()["items"][0]))
        self.assertTrue("description" in list(response.json()["items"][0]))
        self.assertTrue("text" in list(response.json()["items"][0]))
        self.assertEqual(
            {
                u"data": u"<p>Lorem ipsum.</p>",
                u"content-type": u"text/plain",
                u"encoding": u"utf-8",
            },
            response.json()["items"][0].get("text"),
        )

        # make sure the single document response is the same as the items
        response_doc = requests.get(
            self.portal.folder1.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        self.assertEqual(response.json()["items"][0], response_doc.json())

    def test_get_content_include_items(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + "?include_items=false",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("items", response.json())

    def test_get_content_returns_fullobjects_correct_id(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + "?fullobjects",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(3, len(response.json()["items"]))
        self.assertEqual(
            response.json()["items"][1]["@id"], self.portal_url + u"/folder1/folder2"
        )

    def test_get_content_returns_fullobjects_non_recursive(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + "?fullobjects",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(3, len(response.json()["items"]))
        self.assertTrue("items" not in response.json()["items"][1])

    def test_get_content_includes_related_items(self):
        intids = getUtility(IIntIds)
        self.portal.folder1.doc1.relatedItems = [
            RelationValue(intids.getId(self.portal.folder1.folder2.doc2))
        ]
        transaction.commit()
        response = requests.get(
            self.portal.folder1.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(response.json()["relatedItems"]))
        self.assertEqual(
            [
                {
                    u"@id": self.portal_url + u"/folder1/folder2/doc2",
                    u"@type": u"Document",
                    u"description": u"",
                    u"review_state": u"published",
                    u"title": u"My Document 2",
                }
            ],
            response.json()["relatedItems"],
        )

    def test_get_content_related_items_without_workflow(self):
        intids = getUtility(IIntIds)

        self.portal.invokeFactory("Image", id="imagewf")
        self.portal.imagewf.title = "Image without workflow"
        self.portal.imagewf.description = u"This is an image"
        image_file = os.path.join(os.path.dirname(__file__), u"image.png")
        with open(image_file, "rb") as f:
            image_data = f.read()
        self.portal.imagewf.image = NamedBlobImage(
            data=image_data, contentType="image/png", filename=u"image.png"
        )
        transaction.commit()

        self.portal.folder1.doc1.relatedItems = [
            RelationValue(intids.getId(self.portal.imagewf))
        ]
        transaction.commit()
        response = requests.get(
            self.portal.folder1.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(response.json()["relatedItems"]))
        self.assertEqual(
            [
                {
                    u"@id": self.portal_url + u"/imagewf",
                    u"@type": u"Image",
                    u"description": u"This is an image",
                    u"review_state": None,
                    u"title": u"Image without workflow",
                }
            ],
            response.json()["relatedItems"],
        )


class TestContentATGet(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_FUNCTIONAL_TESTING

    def setUp(self):
        if not HAS_AT:
            raise unittest.SkipTest("Skip tests if Archetypes is not present")
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory("Folder", id="folder1", title="My Folder")
        self.portal.folder1.invokeFactory("Document", id="doc1", title="My Document")
        self.portal.folder1.doc1.setText(u"Lorem ipsum.")
        self.portal.folder1.invokeFactory("Folder", id="folder2", title="My Folder 2")
        self.portal.folder1.folder2.invokeFactory(
            "Document", id="doc2", title="My Document 2"
        )
        self.portal.folder1.invokeFactory(
            "Collection", id="collection", title="My collection"
        )
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(self.portal.folder1, "publish")
        wftool.doActionFor(self.portal.folder1.doc1, "publish")
        wftool.doActionFor(self.portal.folder1.folder2, "publish")
        wftool.doActionFor(self.portal.folder1.folder2.doc2, "publish")
        transaction.commit()

    def test_get_content_returns_fullobjects(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + "?fullobjects",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(3, len(response.json()["items"]))
        self.assertTrue("title" in list(response.json()["items"][0]))
        self.assertTrue("description" in list(response.json()["items"][0]))
        self.assertTrue("text" in list(response.json()["items"][0]))
        self.assertEqual(
            {u"data": u"<p>Lorem ipsum.</p>", u"content-type": u"text/html"},
            response.json()["items"][0].get("text"),
        )

        # make sure the single document response is the same as the items
        response_doc = requests.get(
            self.portal.folder1.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        self.assertEqual(response.json()["items"][0], response_doc.json())

    def test_get_content_returns_fullobjects_correct_id(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + "?fullobjects",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(3, len(response.json()["items"]))
        self.assertEqual(
            response.json()["items"][1]["@id"], self.portal_url + u"/folder1/folder2"
        )

    def test_get_content_returns_fullobjects_non_recursive(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + "?fullobjects",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(3, len(response.json()["items"]))
        self.assertTrue("items" not in response.json()["items"][1])
