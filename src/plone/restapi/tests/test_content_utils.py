# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi import HAS_AT
from plone.restapi.services.content.utils import add
from plone.restapi.services.content.utils import create
from plone.restapi.testing import PLONE_RESTAPI_AT_INTEGRATION_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from zExceptions import Unauthorized
from zope.component import getGlobalSiteManager
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent

import unittest


class TestCreateContent(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.folder = self.portal[
            self.portal.invokeFactory("Folder", id="folder", title="My Folder")
        ]

    def test_create_content_with_provided_id(self):
        obj = create(self.folder, "Document", "my-document")
        self.assertEqual(obj.portal_type, "Document")
        self.assertEqual(obj.getId(), "my-document")

    def test_create_content_without_provided_id(self):
        obj = create(self.folder, "Document")
        self.assertEqual(obj.portal_type, "Document")
        self.assertTrue(obj.getId().startswith("document."))

    def test_create_content_without_add_permission_raises_unauthorized(self):
        self.folder.manage_permission(
            "plone.app.contenttypes: Add Document", [], acquire=False
        )
        with self.assertRaises(Unauthorized):
            create(self.folder, "Document", "my-document")

    def test_create_of_disallowed_content_type_raises_unauthorized(self):
        self.portal.portal_types.Folder.filter_content_types = True
        self.portal.portal_types.Folder.allowed_content_types = ()
        with self.assertRaises(Unauthorized):
            create(self.folder, "Document", "my-document")

    def test_create_of_constrained_content_type_raises_unauthorized(self):
        constrains = ISelectableConstrainTypes(self.folder)
        constrains.setConstrainTypesMode(1)
        constrains.setLocallyAllowedTypes(["File"])
        with self.assertRaises(Unauthorized):
            create(self.folder, "Document", "my-document")


class TestATCreateContent(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        if not HAS_AT:
            raise unittest.SkipTest("Skip tests if Archetypes is not present")
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        self.folder = self.portal[
            self.portal.invokeFactory("Folder", id="folder", title="My Folder")
        ]

    def test_create_content_with_provided_id(self):
        obj = create(self.folder, "Document", "my-document")
        self.assertEqual(obj.portal_type, "Document")
        self.assertEqual(obj.getId(), "my-document")

    def test_create_content_without_provided_id(self):
        obj = create(self.folder, "Document")
        self.assertEqual(obj.portal_type, "Document")
        self.assertTrue(obj.getId().startswith("document."))

    def test_create_content_without_add_permission_raises_unauthorized(self):
        self.folder.manage_permission("ATContentTypes: Add Document", [], acquire=False)
        with self.assertRaises(Unauthorized):
            create(self.folder, "Document", "my-document")

    def test_create_of_disallowed_content_type_raises_unauthorized(self):
        self.portal.portal_types.Folder.filter_content_types = True
        self.portal.portal_types.Folder.allowed_content_types = ()
        with self.assertRaises(Unauthorized):
            create(self.folder, "Document", "my-document")

    def test_create_of_constrained_content_type_raises_unauthorized(self):
        constrains = ISelectableConstrainTypes(self.folder)
        constrains.setConstrainTypesMode(1)
        constrains.setLocallyAllowedTypes(["File"])
        with self.assertRaises(Unauthorized):
            create(self.folder, "Document", "my-document")


class TestAddContent(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.folder = self.portal[
            self.portal.invokeFactory("Folder", id="folder", title="My Folder")
        ]

    def test_add_content_to_container(self):
        obj = create(self.folder, "Document", "my-document")
        obj = add(self.folder, obj)
        self.assertEqual(aq_parent(obj), self.folder)

    def test_add_content_to_container_renames_id(self):
        obj = create(self.folder, "Document", title="My Document")
        obj = add(self.folder, obj)
        self.assertEqual(obj.getId(), "my-document")

    def test_add_content_to_container_keeps_id(self):
        obj = create(self.folder, "Document", "doc-1", "My Document")
        obj = add(self.folder, obj, rename=False)
        self.assertEqual(obj.getId(), "doc-1")

    def test_add_content_to_container_and_move_on_added_event(self):
        sm = getGlobalSiteManager()

        def move_object(event):
            self.portal.manage_pasteObjects(
                cb_copy_data=self.folder.manage_cutObjects(ids=["my-document"])
            )

        sm.registerHandler(move_object, (IObjectAddedEvent,))

        obj = create(self.folder, "Document", "my-document")
        notify(ObjectCreatedEvent(obj))
        obj = add(self.folder, obj)
        self.assertEqual(aq_parent(obj), self.portal)

        sm.unregisterHandler(move_object, (IObjectAddedEvent,))


class TestATAddContent(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        if not HAS_AT:
            raise unittest.SkipTest("Skip tests if Archetypes is not present")
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        self.folder = self.portal[
            self.portal.invokeFactory("Folder", id="folder", title="My Folder")
        ]

    def test_add_content_to_container(self):
        obj = create(self.folder, "Document", "my-document")
        obj = add(self.folder, obj)
        self.assertEqual(aq_parent(obj), self.folder)

    def test_add_content_to_container_renames_id(self):
        obj = create(self.folder, "Document", title="My Document")
        obj = add(self.folder, obj)
        self.assertEqual(obj.getId(), "my-document")

    def test_add_content_to_container_keeps_id(self):
        obj = create(self.folder, "Document", "doc-1", "My Document")
        obj = add(self.folder, obj, rename=False)
        self.assertEqual(obj.getId(), "doc-1")
