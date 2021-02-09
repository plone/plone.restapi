# -*- coding: utf-8 -*-

from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import ISlotStorage
from plone.restapi.slots import Slot
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


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

        self.doc = self.portal['folder1']['doc11']

        rootstore = ISlotStorage(self.portal)
        rootstore['left'] = Slot(**({
            'slot_blocks': {
                1: {'title': 'First'},
                3: {'title': 'Third'},
                5: {'title': 'Fifth'},
            },
            'slot_blocks_layout': {'items': [5, 1, 3]}
        }))
        rootstore['right'] = Slot(**({
            'slot_blocks': {
                6: {'title': 'First'},
                7: {'title': 'Third'},
                8: {'title': 'Fifth'},
            },
            'slot_blocks_layout': {'items': [8, 6, 7]}
        }))

        storage = ISlotStorage(self.doc)
        storage['left'] = Slot(
            slot_blocks={2: {'s:isVariantOf': 1, 'title': 'Second'}},
            slot_blocks_layout={'items': [3, 2]},
        )

        setRoles(self.portal, TEST_USER_ID, ["Member"])

    def test_slots_endpoint(self):
        response = self.api_session.get("/@slots")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            u'@id': u'http://localhost:55001/plone/@slots',
            u'edit_slots': [u'right', u'left'],
            u'items': {u'left': {u'@id': u'http://localhost:55001/plone/@slots/left',
                                 u'slot_blocks': {u'1': {u'title': u'First'},
                                                  u'3': {u'title': u'Third'},
                                                  u'5': {u'title': u'Fifth'}},
                                 u'slot_blocks_layout': {u'items': [5, 1, 3]}},
                       u'right': {u'@id': u'http://localhost:55001/plone/@slots/right',
                                  u'slot_blocks': {u'6': {u'title': u'First'},
                                                   u'7': {u'title': u'Third'},
                                                   u'8': {u'title': u'Fifth'}},
                                  u'slot_blocks_layout': {u'items': [8, 6, 7]}}}}
        )

    def test_slot_endpoint(self):
        response = self.api_session.get("/@slots/unregistered")
        self.assertEqual(response.status_code, 404)

    def test_slot_endpoint_on_root(self):
        response = self.api_session.get("/@slots/left")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            u'@id': u'http://localhost:55001/plone/@slots/left',
            u'edit': True,
            u'slot_blocks': {u'1': {u'title': u'First'},
                             u'3': {u'title': u'Third'},
                             u'5': {u'title': u'Fifth'}},
            u'slot_blocks_layout': {u'items': [5, 1, 3]}})
