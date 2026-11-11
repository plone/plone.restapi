from AccessControl.SecurityManagement import getSecurityManager
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.upgrade.utils import loadMigrationProfile
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from unittest import TestCase


class TestUpgrades(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_migration_profile_to_0002_can_be_loaded(self):
        loadMigrationProfile(self.portal, "profile-plone.restapi.upgrades:0002")
        self.assertTrue(True)

    def test_run_migration_profile_to_0002(self):
        from plone.restapi.upgrades.to0002 import assign_use_api_permission

        portal_setup = getToolByName(self.portal, "portal_setup")
        assign_use_api_permission(portal_setup)
        self.assertTrue(True)

    def test_migration_profile_to_0004_can_be_loaded(self):
        loadMigrationProfile(self.portal, "profile-plone.restapi.upgrades:0004")
        self.assertTrue(True)

    def test_run_migration_profile_to_0004(self):
        from plone.restapi.upgrades.to0004 import assign_get_users_permission

        portal_setup = getToolByName(self.portal, "portal_setup")
        assign_get_users_permission(portal_setup)
        self.assertTrue(True)

    def test_run_migration_profile_to_0005(self):
        from plone.restapi.upgrades.to0005 import rename_tiles_to_blocks

        portal_setup = getToolByName(self.portal, "portal_setup")
        rename_tiles_to_blocks(portal_setup)
        self.assertTrue(True)

    def previous_state_0007(self):
        self.portal.manage_permission(
            "plone.restapi: Access Plone user information",
            roles=["Manager"],
            acquire=1,
        )

    def test_previous_state_0007(self):
        self.previous_state_0007()
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        sm = getSecurityManager()
        self.assertIsNone(
            sm.checkPermission(
                "plone.restapi: Access Plone user information", self.portal
            )
        )

    def test_run_migration_profile_to_0007(self):
        self.previous_state_0007()
        from plone.restapi.upgrades.to0007 import site_administrator_permission

        portal_setup = getToolByName(self.portal, "portal_setup")
        site_administrator_permission(portal_setup)

        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        sm = getSecurityManager()
        self.assertTrue(
            sm.checkPermission(
                "plone.restapi: Access Plone user information", self.portal
            )
        )
