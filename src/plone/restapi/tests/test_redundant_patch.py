from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from zope.component import getGlobalSiteManager
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import requests
import transaction
import unittest

class TestRedundantPatch(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Member", "Manager"])
        login(self.portal, SITE_OWNER_NAME)
        transaction.commit()

    def test_patch_image_redundant_no_event(self):
        image_data = "R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs="
        response = requests.post(
            self.portal.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Image",
                "image": {
                    "data": image_data,
                    "encoding": "base64",
                    "content-type": "image/gif",
                    "filename": "test.gif"
                },
            },
        )
        self.assertEqual(201, response.status_code)
        image_url = response.json()["@id"]
        transaction.commit()

        # Track ObjectModifiedEvent
        sm = getGlobalSiteManager()
        fired_events = []

        def record_event(event):
            fired_events.append(event)

        sm.registerHandler(record_event, (IObjectModifiedEvent,))

        # Patch with same data
        response = requests.patch(
            image_url,
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "image": {
                    "data": image_data,
                    "encoding": "base64",
                    "content-type": "image/gif",
                    "filename": "test.gif"
                },
            },
        )
        self.assertEqual(204, response.status_code)
        
        # In current Plone, this will be 1 because of identity mismatch
        # We want it to be 0
        self.assertEqual(len(fired_events), 0, "ObjectModifiedEvent was fired for redundant PATCH")

        sm.unregisterHandler(record_event, (IObjectModifiedEvent,))
