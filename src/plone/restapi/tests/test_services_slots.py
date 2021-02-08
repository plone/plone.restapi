# -*- coding: utf-8 -*-

from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


# from Products.CMFPlone.tests import dummy
# from zope.component import getUtility
# from zope.interface import directlyProvides
# from zope.interface import noLongerProvides


class TestServicesSlots(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
    maxDiff = None

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.populateSite()
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def populateSite(self):
        """
        Portal
        +-doc1
        +-doc2
        +-doc3
        +-folder1
          +-doc11
          +-doc12
          +-doc13
        +-link1
        +-folder2
          +-doc21
          +-doc22
          +-doc23
          +-file21
          +-folder21
            +-doc211
            +-doc212
        """
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        if "Members" in self.portal:
            self.portal._delObject("Members")
            self.folder = None
        if "news" in self.portal:
            self.portal._delObject("news")
        if "events" in self.portal:
            self.portal._delObject("events")
        if "front-page" in self.portal:
            self.portal._delObject("front-page")
        if "folder" in self.portal:
            self.portal._delObject("folder")
        if "users" in self.portal:
            self.portal._delObject("users")

        self.portal.invokeFactory("Document", "doc1")
        self.portal.invokeFactory("Document", "doc2")
        self.portal.invokeFactory("Document", "doc3")
        self.portal.invokeFactory("Folder", "folder1")
        self.portal.invokeFactory("Link", "link1")
        self.portal.link1.remoteUrl = "http://plone.org"
        self.portal.link1.reindexObject()
        folder1 = getattr(self.portal, "folder1")
        folder1.invokeFactory("Document", "doc11")
        folder1.invokeFactory("Document", "doc12")
        folder1.invokeFactory("Document", "doc13")
        self.portal.invokeFactory("Folder", "folder2")
        folder2 = getattr(self.portal, "folder2")
        folder2.invokeFactory("Document", "doc21")
        folder2.invokeFactory("Document", "doc22")
        folder2.invokeFactory("Document", "doc23")
        folder2.invokeFactory("File", "file21")
        folder2.invokeFactory("Folder", "folder21")
        folder21 = getattr(folder2, "folder21")
        folder21.invokeFactory("Document", "doc211")
        folder21.invokeFactory("Document", "doc212")

        setRoles(self.portal, TEST_USER_ID, ["Member"])

    def test_slots_endpoint(self):
        response = self.api_session.get("/@slots")
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response, {
            "@id": "http://localhost:55001/plone/@slots",
            "items": {}
        })
