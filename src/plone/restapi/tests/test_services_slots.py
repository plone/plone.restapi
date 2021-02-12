# -*- coding: utf-8 -*-

from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.slots import Slot
from plone.restapi.slots.interfaces import ISlotStorage
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
        self.setup_slots()
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def populateSite(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.portal.invokeFactory("Folder", "folder1")
        folder1 = getattr(self.portal, "folder1")
        folder1.invokeFactory("Document", "doc11")

        self.doc = self.portal["folder1"]["doc11"]

        setRoles(self.portal, TEST_USER_ID, ["Member"])

    def setup_slots(self):
        rootstore = ISlotStorage(self.portal)
        rootstore[u"left"] = Slot()
        rootstore[u"left"].blocks = {
            u"1": {"title": "First"},
            u"3": {"title": "Third"},
            u"5": {"title": "Fifth"},
        }
        rootstore[u"left"].blocks_layout = {"items": [u"5", u"1", u"3"]}

        rootstore[u"right"] = Slot()
        rootstore[u"right"].blocks = {
            u"6": {"title": "First"},
            u"7": {"title": "Third"},
            u"8": {"title": "Fifth"},
        }
        rootstore[u"right"].blocks_layout = {"items": [u"8", u"6", u"7"]}

        storage = ISlotStorage(self.doc)
        storage[u"left"] = Slot()
        storage[u"left"].blocks = {u"2": {"s:isVariantOf": u"1", "title": "Second"}}
        storage[u"left"].blocks_layout = {"items": [u"3", u"2"]}

    def test_slots_endpoint(self):
        response = self.api_session.get("/@slots")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                u"@id": u"http://localhost:55001/plone/@slots",
                u"edit_slots": [u"left", u"right"],
                u"items": {
                    u"left": {
                        u"@id": u"http://localhost:55001/plone/@slots/left",
                        u"blocks": {
                            u"1": {u"title": u"First"},
                            u"3": {u"title": u"Third"},
                            u"5": {u"title": u"Fifth"},
                        },
                        u"blocks_layout": {u"items": [u"5", u"1", u"3"]},
                    },
                    u"right": {
                        u"@id": u"http://localhost:55001/plone/@slots/right",
                        u"blocks": {
                            u"6": {u"title": u"First"},
                            u"7": {u"title": u"Third"},
                            u"8": {u"title": u"Fifth"},
                        },
                        u"blocks_layout": {u"items": [u"8", u"6", u"7"]},
                    },
                },
            },
        )

    def test_slot_endpoint(self):
        response = self.api_session.get("/@slots/unregistered")
        self.assertEqual(response.status_code, 404)

    def test_slot_endpoint_on_root(self):
        response = self.api_session.get("/@slots/left")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                u"@id": u"http://localhost:55001/plone/@slots/left",
                u"edit": True,
                u"blocks": {
                    u"1": {u"title": u"First"},
                    u"3": {u"title": u"Third"},
                    u"5": {u"title": u"Fifth"},
                },
                u"blocks_layout": {u"items": [u"5", u"1", u"3"]},
            },
        )

    def test_deserializer_on_slot(self):
        response = self.api_session.patch("/@slots/left", json={})
        self.assertEqual(response.status_code, 204)

    def test_deserializer_on_slot_with_data_and_missing_slots(self):
        response = self.api_session.patch(
            "/@slots/left",
            json={
                "blocks": {
                    u"1": {"title": "First"},
                },
                "blocks_layout": {"items": [u"5", u"1", u"3"]},
            },
        )
        transaction.commit()
        self.assertEqual(response.status_code, 204)
        storage = ISlotStorage(self.portal)
        self.assertEqual(
            storage["left"].blocks,
            {
                u"1": {"title": "First"},
            },
        )
        self.assertEqual(storage["left"].blocks_layout, {"items": [u"1"]})
