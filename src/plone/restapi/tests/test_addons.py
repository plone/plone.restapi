# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import unittest


class TestAddons(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_get_addon_record(self):
        response = self.api_session.get("/@addons/plone.session")

        self.assertEqual(response.status_code, 200)
        result = response.json()

        self.assertEqual(result["@id"], self.portal_url + u"/@addons/plone.session")
        self.assertEqual(result["id"], u"plone.session")
        # self.assertEqual(result['is_installed'], False)
        self.assertEqual(result["title"], u"Session refresh support")
        self.assertEqual(
            result["description"], u"Optional plone.session refresh support."
        )
        self.assertEqual(result["profile_type"], u"default")
        self.assertEqual(result["upgrade_info"], {})
        self.assertEqual(result["install_profile_id"], u"plone.session:default")

    def test_get_addon_listing(self):
        response = self.api_session.get("/@addons")

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIn("items", response)

    def test_install_uninstall_addon(self):
        def _get_install_status(self):
            response = self.api_session.get("/@addons/plone.session")
            result = response.json()
            return result["is_installed"]

        # Check to make sure the addon is currently shown as not installed
        self.assertEqual(_get_install_status(self), False)

        response = self.api_session.post("/@addons/plone.session/install")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, "")

        # Check to make sure the addon is currently shown as installed
        self.assertEqual(_get_install_status(self), True)

        # Now uninstall the addon
        response = self.api_session.post("/@addons/plone.session/uninstall")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, "")
        # Check to make sure the addon is currently shown as not installed
        self.assertEqual(_get_install_status(self), False)

    def test_install_uninstall_addon_with_representation(self):

        # Check to make sure the addon is currently shown as not installed
        response = self.api_session.get("/@addons/plone.session")
        result = response.json()
        self.assertEqual(result["is_installed"], False)

        # Install the addon
        response = self.api_session.post(
            "/@addons/plone.session/install",
            headers={"Prefer": "return=representation"},
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()

        # Check to make sure the addon is currently shown as installed
        session = [a for a in result["items"] if a["id"] == u"plone.session"]
        self.assertEqual(len(session), 1)
        self.assertTrue(session[0]["is_installed"])

        # Now uninstall the addon
        response = self.api_session.post(
            "/@addons/plone.session/uninstall",
            headers={"Prefer": "return=representation"},
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()
        # Check to make sure the addon is currently shown as not installed
        session = [a for a in result["items"] if a["id"] == u"plone.session"]
        self.assertEqual(len(session), 1)
        self.assertFalse(session[0]["is_installed"])

    def test_upgrade_addon(self):
        response = self.api_session.post("/@addons/plone.session/upgrade")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, "")

        self.fail("Not finished yet")

    def test_upgrade_addon_with_representation(self):
        response = self.api_session.post(
            "/@addons/plone.session/upgrade",
            headers={"Prefer": "return=representation"},
        )

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.fail("Not finished yet")
