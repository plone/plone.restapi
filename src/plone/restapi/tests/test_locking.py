# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import INonStealableLock
from plone.locking.interfaces import ITTWLockable
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.interface import alsoProvides

import transaction
import unittest


class TestLocking(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        login(self.portal, SITE_OWNER_NAME)
        self.doc = self.portal[
            self.portal.invokeFactory("Document", id="doc1", title="My Document")
        ]
        alsoProvides(self.doc, ITTWLockable)

        self.api_session = RelativeSession(self.doc.absolute_url())
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_lock_object(self):
        response = self.api_session.post("/@lock")
        transaction.commit()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ILockable(self.doc).locked())

    def test_lock_object_non_stealable(self):
        response = self.api_session.post("/@lock", json={"stealable": False})
        transaction.commit()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(INonStealableLock.providedBy(self.doc))

    def test_lock_object_with_custom_timeout(self):
        response = self.api_session.post("/@lock", json={"timeout": 86400})
        transaction.commit()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.doc.wl_lockValues()[0].getTimeout(), 86400)

    def test_unlock_object(self):
        lockable = ILockable(self.doc)
        lockable.lock()
        transaction.commit()
        response = self.api_session.post("/@unlock")
        transaction.commit()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(lockable.locked())

    def test_refresh_lock(self):
        lockable = ILockable(self.doc)
        lockable.lock()
        modified = self.doc.wl_lockValues()[0].getModifiedTime()
        transaction.commit()
        response = self.api_session.post("/@refresh-lock")
        transaction.commit()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.doc.wl_lockValues()[0].getModifiedTime() > modified)

    def test_lock_info_for_locked_object(self):
        lockable = ILockable(self.doc)
        lockable.lock()
        transaction.commit()
        response = self.api_session.get("/@lock")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["locked"])

    def test_lock_info_for_unlocked_object(self):
        response = self.api_session.get("/@lock")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["locked"])

    def test_update_locked_object_without_token_fails(self):
        lockable = ILockable(self.doc)
        lockable.lock()
        transaction.commit()
        response = self.api_session.patch("/", json={"title": "New Title"})
        transaction.commit()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.doc.Title(), "My Document")

    def test_update_locked_object_with_token_succeeds(self):
        lockable = ILockable(self.doc)
        lockable.lock()
        transaction.commit()
        response = self.api_session.patch(
            "/",
            headers={"Lock-Token": lockable.lock_info()[0]["token"]},
            json={"title": "New Title"},
        )
        transaction.commit()
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.doc.Title(), "New Title")
