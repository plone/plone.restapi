from OFS.interfaces import IObjectWillBeAddedEvent
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import getToolByName
from zope.component import getGlobalSiteManager
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import json
import requests
import transaction
import unittest


class TestContentPatch(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory(
            "Document", id="doc1", title="My Document", description="Some Description"
        )
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(self.portal.doc1, "publish")
        transaction.commit()

    def test_patch_document(self):
        response = requests.patch(
            self.portal.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            data='{"title": "Patched Document"}',
        )
        self.assertEqual(204, response.status_code)
        transaction.begin()
        self.assertEqual("Patched Document", self.portal.doc1.Title())

    def test_patch_document_will_delete_value_with_null(self):
        self.assertEqual(self.portal.doc1.description, "Some Description")
        response = requests.patch(
            self.portal.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            data='{"description": null}',
        )
        transaction.commit()

        # null will set field.missing_value which is u'' for the field
        self.assertEqual(204, response.status_code)
        self.assertEqual("", self.portal.doc1.description)

    def test_patch_document_will_not_delete_value_with_null_if_required(self):
        response = requests.patch(
            self.portal.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            data='{"title": null}',
        )
        transaction.commit()

        # null will set field.missing_value which is u'' for the field
        self.assertEqual(400, response.status_code)
        self.assertTrue("'field': 'title'" in response.text)
        self.assertTrue("title is a required field." in response.text)
        self.assertTrue("Setting it to null is not allowed." in response.text)

    def test_patch_document_with_representation(self):
        response = requests.patch(
            self.portal.doc1.absolute_url(),
            headers={"Accept": "application/json", "Prefer": "return=representation"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            data='{"title": "Patched Document"}',
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json()["title"], "Patched Document")
        transaction.begin()
        self.assertEqual("Patched Document", self.portal.doc1.Title())

    def test_patch_document_with_invalid_body_returns_400(self):
        response = requests.patch(
            self.portal.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            data="foo",
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("DeserializationError", response.text)

    def test_patch_undeserializable_object_returns_501(self):
        obj = PortalContent()
        obj.id = "obj1"
        obj.portal_type = "Undeserializable Type"
        self.portal._setObject(obj.id, obj)
        transaction.commit()

        response = requests.patch(
            self.portal.obj1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            data='{"id": "patched_obj1"}',
        )
        self.assertEqual(501, response.status_code)
        self.assertIn("Undeserializable Type", response.text)

    def test_patch_document_returns_401_unauthorized(self):
        response = requests.patch(
            self.portal.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            data='{"title": "Patched Document"}',
        )
        self.assertEqual(401, response.status_code)

    def test_patch_image_with_the_contents_of_the_get_preserves_image(self):
        response = requests.post(
            self.portal.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Image",
                "image": {
                    "data": "R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=",  # noqa
                    "encoding": "base64",
                    "content-type": "image/gif",
                },
            },
        )
        transaction.commit()

        response = response.json()
        image_url = self.portal[response["id"]].absolute_url()
        response = requests.patch(
            image_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json=response,
        )
        transaction.commit()
        response = requests.get(image_url, headers={"Accept": "application/json"})

        self.assertTrue(response.json()["image"])
        self.assertIn("content-type", response.json()["image"])
        self.assertIn("download", response.json()["image"])

    def test_patch_document_fires_proper_events(self):
        sm = getGlobalSiteManager()
        fired_events = []

        def record_event(event):
            fired_events.append(event.__class__.__name__)

        sm.registerHandler(record_event, (IObjectCreatedEvent,))
        sm.registerHandler(record_event, (IObjectWillBeAddedEvent,))
        sm.registerHandler(record_event, (IObjectAddedEvent,))
        sm.registerHandler(record_event, (IObjectModifiedEvent,))

        requests.patch(
            self.portal.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"description": "123"},
        )

        self.assertEqual(fired_events, ["ObjectModifiedEvent"])

        sm.unregisterHandler(record_event, (IObjectCreatedEvent,))
        sm.unregisterHandler(record_event, (IObjectWillBeAddedEvent,))
        sm.unregisterHandler(record_event, (IObjectAddedEvent,))
        sm.unregisterHandler(record_event, (IObjectModifiedEvent,))

    def test_patch_document_with_apostrophe_dont_return_500(self):
        data = {
            "text": {
                "content-type": "text/html",
                "encoding": "utf8",
                "data": "<p>example with &#x27;</p>",
            }
        }
        response = requests.patch(
            self.portal.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            data=json.dumps(data),
        )
        self.assertEqual(204, response.status_code)
        transaction.begin()
        self.assertEqual("<p>example with '</p>", self.portal.doc1.text.raw)
