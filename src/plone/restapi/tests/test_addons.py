from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

import transaction
import unittest


class TestAddons(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.ps = getToolByName(self.portal, "portal_setup")
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_get_addon_record(self):
        response = self.api_session.get("/@addons/plone.session")

        self.assertEqual(response.status_code, 200)
        result = response.json()

        self.assertEqual(result["@id"], self.portal_url + "/@addons/plone.session")
        self.assertEqual(result["id"], "plone.session")
        # self.assertEqual(result['is_installed'], False)
        self.assertEqual(result["title"], "Session refresh support")
        self.assertEqual(
            result["description"], "Optional plone.session refresh support."
        )
        self.assertEqual(result["profile_type"], "default")
        self.assertEqual(result["upgrade_info"], {})
        self.assertEqual(result["install_profile_id"], "plone.session:default")

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
        self.assertEqual(safe_unicode(response.content), "")

        # Check to make sure the addon is currently shown as installed
        self.assertEqual(_get_install_status(self), True)

        # Now uninstall the addon
        response = self.api_session.post("/@addons/plone.session/uninstall")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(safe_unicode(response.content), "")

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
        session = [a for a in result["items"] if a["id"] == "plone.session"]
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
        session = [a for a in result["items"] if a["id"] == "plone.session"]
        self.assertEqual(len(session), 1)
        self.assertFalse(session[0]["is_installed"])

    def test_upgrade_addon(self):
        def _get_upgrade_info(self):
            response = self.api_session.get("/@addons/plone.restapi")
            result = response.json()
            return result["upgrade_info"]

        # Set need upgrade state
        self.ps.setLastVersionForProfile("plone.restapi:default", "0002")
        transaction.commit()
        self.assertEqual(
            {
                "available": True,
                "hasProfile": True,
                "installedVersion": "0002",
                "newVersion": "0006",
                "required": True,
            },
            _get_upgrade_info(self),
        )

        # Now call the upgrade
        response = self.api_session.post("/@addons/plone.restapi/upgrade")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(safe_unicode(response.content), "")
        self.assertEqual(
            {
                "available": False,
                "hasProfile": True,
                "installedVersion": "0006",
                "newVersion": "0006",
                "required": False,
            },
            _get_upgrade_info(self),
        )

    def test_upgrade_addon_with_representation(self):
        response = self.api_session.get("/@addons/plone.restapi")
        result = response.json()
        last_version = result["upgrade_info"]

        # Set need upgrade state
        self.ps.setLastVersionForProfile("plone.restapi:default", "0002")
        transaction.commit()
        response = self.api_session.get("/@addons/plone.restapi")
        result = response.json()
        self.assertEqual(
            {
                "available": True,
                "hasProfile": True,
                "installedVersion": "0002",
                "newVersion": last_version["newVersion"],
                "required": True,
            },
            result["upgrade_info"],
        )

        # Now call the upgrade
        response = self.api_session.post(
            "/@addons/plone.restapi/upgrade",
            headers={"Prefer": "return=representation"},
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()

        # Check to make sure the addon is at last version
        session = [a for a in result["items"] if a["id"] == "plone.restapi"]
        self.assertEqual(len(session), 1)
        self.assertEqual(last_version, session[0]["upgrade_info"])

    def test_get_only_upgradeables(self):
        def _get_upgrade_info(self):
            response = self.api_session.get("/@addons/plone.restapi")
            result = response.json()
            return result["upgrade_info"]

        # Set need upgrade state
        self.ps.setLastVersionForProfile("plone.restapi:default", "0002")
        transaction.commit()
        self.assertEqual(
            {
                "available": True,
                "hasProfile": True,
                "installedVersion": "0002",
                "newVersion": "0006",
                "required": True,
            },
            _get_upgrade_info(self),
        )

        response = self.api_session.get("/@addons?upgradeable=1")

        self.assertEqual(1, len(response.json()["items"]))
        self.assertEqual("plone.restapi", response.json()["items"][0]["id"])

    def test_install_specific_profile(self):
        response = self.api_session.post(
            "/@addons/plone.restapi/import/testing-workflows"
        )
        self.assertEqual(response.status_code, 204)

        transaction.commit()

        # This test installs the profile 'testing-workflows', which installs
        # a workflow named "restriction_workflow", we check for it to be present
        pw = api.portal.get_tool("portal_workflow")
        self.assertIn("restriction_workflow", pw.listWorkflows())
