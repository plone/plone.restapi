# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import unittest


try:
    from Products.CMFPlone.factory import _IMREALLYPLONE5  # noqa
except ImportError:
    PLONE5 = False
else:
    PLONE5 = True


@unittest.skipIf(not PLONE5, "Just Plone 5 currently.")
class TestControlpanelsEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_get_listing(self):
        # Do we get a list with at least one item?
        response = self.api_session.get("/@controlpanels")
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertIs(type(data), list)
        self.assertGreater(len(data), 0)

    def test_get_item_nonexisting(self):
        response = self.api_session.get("/@controlpanels/no-way-jose")
        self.assertEqual(404, response.status_code)

    def test_get_item(self):
        response = self.api_session.get("/@controlpanels/editing")
        self.assertEqual(200, response.status_code)

    def test_all_controlpanels(self):
        # make sure all define controlpanels serialize
        response = self.api_session.get("/@controlpanels")
        for item in response.json():
            response = self.api_session.get(item["@id"])
            self.assertEqual(
                200,
                response.status_code,
                "{} failed: {}".format(item["@id"], response.json()),
            )

    def test_patch_needs_parameter(self):
        response = self.api_session.patch("/@controlpanels")
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            "Missing parameter controlpanelname", response.json()["message"]
        )

    def test_update(self):
        # get current settings, switch them and check if it changed
        response = self.api_session.get("/@controlpanels/editing")
        old_data = response.json()["data"]

        # switch values and set
        new_values = {
            "ext_editor": not old_data["ext_editor"],
            "lock_on_ttw_edit": not old_data["lock_on_ttw_edit"],
        }
        response = self.api_session.patch("/@controlpanels/editing", json=new_values)

        # check if the values changed
        response = self.api_session.get("/@controlpanels/editing")
        self.assertNotEqual(response.json(), old_data)

    def test_update_all(self):
        # Mail is in faulty state by default
        self.api_session.patch(
            "/@controlpanels/mail",
            json={
                "email_from_address": "admin@local.local",
                "email_from_name": "Jos Henken",
            },
        )

        # make sure all define controlpanels deserialize
        response = self.api_session.get("/@controlpanels")
        for item in response.json():
            # get current data
            response = self.api_session.get(item["@id"])

            # store the outputted data
            response = self.api_session.patch(item["@id"], json=response.json()["data"])
            self.assertEqual(
                204,
                response.status_code,
                "{} failed: {}".format(item["@id"], response.content),
            )

    def test_update_required(self):
        KEY = "email_charset"
        URL = "/@controlpanels/mail"
        # sanity check
        response = self.api_session.get(URL)
        response = response.json()
        self.assertIn(KEY, response["schema"]["required"])

        response = self.api_session.patch(URL, json={KEY: None})

        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertIn("message", response)
        self.assertIn("Required input is missing.", response["message"])
