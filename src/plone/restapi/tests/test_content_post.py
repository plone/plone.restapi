from OFS.interfaces import IObjectWillBeAddedEvent
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from Products.CMFCore.utils import getToolByName
from zope.component import getGlobalSiteManager
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import requests
import transaction
import unittest


class TestFolderCreate(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory("Folder", id="folder1", title="My Folder")
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(self.portal.folder1, "publish")
        transaction.commit()

    def test_post_to_folder_creates_document(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"@type": "Document", "id": "mydocument", "title": "My Document"},
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        self.assertEqual("My Document", self.portal.folder1.mydocument.Title())
        self.assertEqual("Document", response.json().get("@type"))
        self.assertEqual("mydocument", response.json().get("id"))
        self.assertEqual("My Document", response.json().get("title"))

        expected_url = self.portal_url + "/folder1/mydocument"
        self.assertEqual(expected_url, response.json().get("@id"))

    def test_post_to_folder_creates_folder(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"@type": "Folder", "id": "myfolder", "title": "My Folder"},
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        self.assertEqual("My Folder", self.portal.folder1.myfolder.Title())
        self.assertEqual("Folder", response.json().get("@type"))
        self.assertEqual("myfolder", response.json().get("id"))
        self.assertEqual("My Folder", response.json().get("title"))

        expected_url = self.portal_url + "/folder1/myfolder"
        self.assertEqual(expected_url, response.json().get("@id"))

    def test_post_without_type_returns_400(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": "mydocument", "title": "My Document"},
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("Property '@type' is required", response.text)

    def test_post_without_id_creates_id_from_title(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"@type": "Document", "title": "My Document"},
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        self.assertIn("my-document", self.portal.folder1)

    def test_post_without_id_creates_id_from_filename(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "File",
                "title": "My File",
                "file": {
                    "filename": "test.txt",
                    "data": "Spam and Eggs",
                    "content_type": "text/plain",
                },
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        self.assertIn("test.txt", self.portal.folder1)

    def test_post_with_id_already_in_use_returns_400(self):
        self.portal.folder1.invokeFactory("Document", "mydocument")
        transaction.commit()
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"@type": "Document", "id": "mydocument", "title": "My Document"},
        )
        self.assertEqual(400, response.status_code)

    def test_post_to_folder_returns_401_unauthorized(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={"@type": "Document", "id": "mydocument", "title": "My Document"},
        )
        self.assertEqual(401, response.status_code)

    def test_post_to_folder_without_add_permission_returns_403_forbidden(self):
        self.portal.folder1.manage_permission(
            "plone.app.contenttypes: Add Document", [], acquire=False
        )
        transaction.commit()
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"@type": "Document", "id": "mydocument", "title": "My Document"},
        )
        self.assertEqual(403, response.status_code)

    def test_post_to_folder_fires_proper_events(self):
        sm = getGlobalSiteManager()
        fired_events = []

        def record_event(event):
            fired_events.append(event.__class__.__name__)

        sm.registerHandler(record_event, (IObjectCreatedEvent,))
        sm.registerHandler(record_event, (IObjectWillBeAddedEvent,))
        sm.registerHandler(record_event, (IObjectAddedEvent,))
        sm.registerHandler(record_event, (IObjectModifiedEvent,))

        requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Document",
                "id": "mydocument",
                "title": "My Document",
                "description": "123",
            },
        )

        self.assertEqual(
            fired_events,
            [
                "ObjectCreatedEvent",
                "ObjectWillBeAddedEvent",
                "ObjectAddedEvent",
                "ContainerModifiedEvent",
            ],
        )

        sm.unregisterHandler(record_event, (IObjectCreatedEvent,))
        sm.unregisterHandler(record_event, (IObjectWillBeAddedEvent,))
        sm.unregisterHandler(record_event, (IObjectAddedEvent,))
        sm.unregisterHandler(record_event, (IObjectModifiedEvent,))

    def test_post_to_folder_with_apostrophe_dont_return_500(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Document",
                "id": "mydocument2",
                "title": "My Document 2",
                "text": {
                    "content-type": "text/html",
                    "encoding": "utf8",
                    "data": "<p>example with &#x27;</p>",
                },
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        self.assertEqual(
            "<p>example with '</p>", self.portal.folder1.mydocument2.text.raw
        )
        self.assertEqual("<p>example with '</p>", response.json()["text"]["data"])

    def test_post_with_uid_with_manage_portal_permission(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Document",
                "title": "My Document",
                "UID": "a9597fcb108c4985a713329311bdcca0",
            },
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.json()["UID"], "a9597fcb108c4985a713329311bdcca0")

    def test_post_with_uid_without_manage_portal_permission(self):
        user = "test-user-2"
        password = "secret"
        self.portal.acl_users.userFolderAddUser(user, password, ["Contributor"], [])
        transaction.commit()

        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(user, password),
            json={
                "@type": "Document",
                "title": "My Document",
                "UID": "a9597fcb108c4985a713329311bdcca0",
            },
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            response.json()["error"]["message"],
            "Setting UID of an object requires Manage Portal permission",
        )
