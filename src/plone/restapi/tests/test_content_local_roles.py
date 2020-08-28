# -*- coding: utf-8 -*-
from Acquisition import aq_base
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.serializer.local_roles import SerializeLocalRolesToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from Products.CMFCore.utils import getToolByName
from zope.component import getGlobalSiteManager

import requests
import transaction
import unittest


def sorted_roles(roles):
    results = []
    for line in roles:
        line = list(line)
        line[1] = sorted(line[1])
        results.append(line)
    return results


class TestFolderCreate(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory("Folder", id="folder1", title="My Folder")
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(self.portal.folder1, "publish")

        self.portal.folder1.invokeFactory("Document", id="doc1", title="My Document")

        transaction.commit()

    def _get_ac_local_roles_block(self, obj):
        return bool(
            getattr(aq_base(self.portal.folder1), "__ac_local_roles_block__", False)
        )

    def test_sharing_search(self):
        """A request to @sharing should support the search parameter. """
        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        non_search_entries = response.json()["entries"]

        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing?search=admin",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        search_entries = response.json()["entries"]

        # Did we find anything?
        self.assertNotEqual(len(non_search_entries), len(search_entries))

    def test_sharing_search_roundtrip(self):
        """Search for a user and use save roles"""
        # Make sure we don't already have admin
        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        self.assertNotIn("admin", [x["id"] for x in response.json()["entries"]])

        # Now find admin and set roles
        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing?search=admin",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        roles = [x for x in response.json()["entries"] if x["id"] == "admin"]
        roles = roles[0]["roles"]

        new_roles = dict([(key, not val) for key, val in roles.items()])
        payload = {"entries": [{"id": "admin", "roles": new_roles}]}

        response = requests.post(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json=payload,
        )
        self.assertEqual(204, response.status_code)

        # Now we should have admin in @sharing
        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        self.assertIn("admin", [x["id"] for x in response.json()["entries"]])

        # with the same roles as set
        roles = [x for x in response.json()["entries"] if x["id"] == "admin"]
        roles = roles[0]["roles"]
        self.assertEqual(new_roles, roles)

    def test_sharing_titles_are_translated(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json", "Accept-Language": "de"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        available_roles = response.json()["available_roles"]
        self.assertEqual(
            [
                {u"id": u"Contributor", u"title": u"Kann hinzuf\xfcgen"},
                {u"id": u"Editor", u"title": u"Kann bearbeiten"},
                {u"id": u"Reader", u"title": u"Kann ansehen"},
                {u"id": u"Reviewer", u"title": u"Kann ver\xf6ffentlichen"},
            ],
            available_roles,
        )

    def test_sharing_requires_delegate_roles_permission(self):
        """A response for an object without any roles assigned"""
        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
        )

        self.assertEqual(response.status_code, 403)

    def test_get_local_roles_none_assigned(self):
        """A response for an object without any roles assigned"""
        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                u"available_roles": [
                    {u"id": u"Contributor", u"title": u"Can add"},
                    {u"id": u"Editor", u"title": u"Can edit"},
                    {u"id": u"Reader", u"title": u"Can view"},
                    {u"id": u"Reviewer", u"title": u"Can review"},
                ],
                u"entries": [
                    {
                        u"disabled": False,
                        u"id": u"AuthenticatedUsers",
                        u"login": None,
                        u"roles": {
                            u"Contributor": False,
                            u"Editor": False,
                            u"Reader": False,
                            u"Reviewer": False,
                        },
                        u"title": u"Logged-in users",
                        u"type": u"group",
                    }
                ],
                u"inherit": True,
            },
        )

    def test_get_local_roles_with_user(self):
        api.user.grant_roles(
            username=TEST_USER_ID, obj=self.portal.folder1, roles=["Reviewer"]
        )
        transaction.commit()

        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                u"available_roles": [
                    {u"id": u"Contributor", u"title": u"Can add"},
                    {u"id": u"Editor", u"title": u"Can edit"},
                    {u"id": u"Reader", u"title": u"Can view"},
                    {u"id": u"Reviewer", u"title": u"Can review"},
                ],
                u"entries": [
                    {
                        u"disabled": False,
                        u"id": u"AuthenticatedUsers",
                        u"login": None,
                        u"roles": {
                            u"Contributor": False,
                            u"Editor": False,
                            u"Reader": False,
                            u"Reviewer": False,
                        },
                        u"title": u"Logged-in users",
                        u"type": u"group",
                    },
                    {
                        u"disabled": False,
                        u"id": u"test_user_1_",
                        u"roles": {
                            u"Contributor": False,
                            u"Editor": False,
                            u"Reader": False,
                            u"Reviewer": True,
                        },
                        u"title": u"test-user",
                        u"type": u"user",
                    },
                ],
                u"inherit": True,
            },
        )

    def test_set_local_roles_for_user(self):

        pas = getToolByName(self.portal, "acl_users")
        self.assertEqual(
            pas.getLocalRolesForDisplay(self.portal.folder1),
            (("admin", ("Owner",), "user", "admin"),),
        )

        response = requests.post(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "entries": [
                    {
                        u"id": TEST_USER_ID,
                        u"roles": {
                            u"Contributor": False,
                            u"Editor": False,
                            u"Reader": True,
                            u"Reviewer": True,
                        },
                        u"type": u"user",
                    }
                ]
            },
        )

        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            sorted_roles(pas.getLocalRolesForDisplay(self.portal.folder1)),
            [
                ["admin", ["Owner"], "user", "admin"],
                ["test-user", [u"Reader", u"Reviewer"], "user", u"test_user_1_"],
            ],
        )

    def test_may_only_manage_roles_already_held(self):
        # Grant Editor role to our test user (which gives them the required
        # "plone.DelegateRoles" permission to manage local roles at all)
        api.user.grant_roles(
            username=TEST_USER_ID, obj=self.portal.folder1, roles=["Editor"]
        )
        transaction.commit()

        # Guard assertion - our test user starts with a limited set of roles
        existing_roles = api.user.get_roles(
            username=TEST_USER_ID, obj=self.portal.folder1
        )
        self.assertEqual(
            sorted(["Member", "Authenticated", "Editor"]), sorted(existing_roles)
        )

        # Attempt to gain additional roles not already held
        response = requests.post(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={
                "entries": [
                    {
                        u"id": TEST_USER_ID,
                        u"roles": {
                            u"Contributor": True,
                            u"Editor": True,
                            u"Reader": True,
                            u"Publisher": True,
                            u"Reviewer": True,
                            u"Manager": True,
                        },
                        u"type": u"user",
                    }
                ]
            },
        )

        transaction.commit()

        self.assertEqual(response.status_code, 204)
        new_roles = api.user.get_roles(username=TEST_USER_ID, obj=self.portal.folder1)

        # New roles should not contain any new roles that the user didn't
        # have permission to delegate.
        self.assertNotIn(u"Manager", new_roles)
        self.assertNotIn(u"Publisher", new_roles)
        self.assertNotIn(u"Reviewer", new_roles)
        self.assertNotIn(u"Contributor", new_roles)

        # 'Reader' gets added because the permission to delegate it is
        # assigned to 'Editor' by default (see p.a.workflow.permissions)
        self.assertEqual(
            sorted(["Member", "Authenticated", "Editor", "Reader"]), sorted(new_roles)
        )

    def test_unmanaged_existing_roles_are_retained_on_update(self):
        """Make sure that existing roles don't get dropped when a user that
        doesn't manage that roles updates local roles for another user that
        already holds that role.
        """
        # Create another user that holds the Reviewer role, which is not
        # managed by our test user
        api.user.create(
            username="peter",
            email="peter@example.org",
            password="secret",
            roles=("Member",),
        )

        api.user.grant_roles(
            username="peter", obj=self.portal.folder1, roles=["Reviewer"]
        )
        transaction.commit()

        peters_existing_roles = api.user.get_roles(
            username="peter", obj=self.portal.folder1
        )
        self.assertEqual(
            sorted(["Member", "Reviewer", "Authenticated"]),
            sorted(peters_existing_roles),
        )

        # Grant Editor role to our test user (which gives them the required
        # "plone.DelegateRoles" permission to manage local roles at all)
        api.user.grant_roles(
            username=TEST_USER_ID, obj=self.portal.folder1, roles=["Editor"]
        )
        transaction.commit()

        # Guard assertion - our test user doesn't have/manage Reviewer
        existing_roles = api.user.get_roles(
            username=TEST_USER_ID, obj=self.portal.folder1
        )
        self.assertEqual(
            sorted(["Member", "Authenticated", "Editor"]), sorted(existing_roles)
        )

        # Test user now gives Editor to peter. This should not lead to
        # peter losing the Reviewer role.
        response = requests.post(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={
                "entries": [
                    {
                        u"id": "peter",
                        u"roles": {
                            u"Contributor": False,
                            u"Editor": True,
                            u"Reader": True,
                            u"Publisher": False,
                            u"Reviewer": True,
                            u"Manager": False,
                        },
                        u"type": u"user",
                    }
                ]
            },
        )

        transaction.commit()

        self.assertEqual(response.status_code, 204)
        new_roles = api.user.get_roles(username="peter", obj=self.portal.folder1)

        self.assertIn(u"Reviewer", new_roles)
        self.assertEqual(
            sorted(["Member", "Authenticated", "Editor", "Reader", "Reviewer"]),
            sorted(new_roles),
        )

    def test_unset_local_roles_for_user(self):
        api.user.grant_roles(
            username=TEST_USER_ID, obj=self.portal.folder1, roles=["Reviewer", "Reader"]
        )
        transaction.commit()

        pas = getToolByName(self.portal, "acl_users")
        self.assertEqual(
            sorted_roles(pas.getLocalRolesForDisplay(self.portal.folder1)),
            [
                ["admin", ["Owner"], "user", "admin"],
                ["test-user", ["Reader", "Reviewer"], "user", "test_user_1_"],
            ],
        )

        response = requests.post(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "entries": [
                    {
                        u"id": TEST_USER_ID,
                        u"roles": {
                            u"Contributor": False,
                            u"Editor": False,
                            u"Reader": False,
                            u"Reviewer": True,
                        },
                        u"type": u"user",
                    }
                ]
            },
        )

        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            pas.getLocalRolesForDisplay(self.portal.folder1),
            (
                ("admin", ("Owner",), "user", "admin"),
                ("test-user", (u"Reviewer",), "user", u"test_user_1_"),
            ),
        )

    def test_set_local_roles_on_site_root(self):

        pas = getToolByName(self.portal, "acl_users")
        self.assertEqual(
            pas.getLocalRolesForDisplay(self.portal),
            (("admin", ("Owner",), "user", "admin"),),
        )

        response = requests.post(
            self.portal.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "entries": [
                    {
                        u"id": TEST_USER_ID,
                        u"roles": {
                            u"Contributor": False,
                            u"Editor": False,
                            u"Reader": True,
                            u"Reviewer": True,
                        },
                        u"type": u"user",
                    }
                ]
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            sorted_roles(pas.getLocalRolesForDisplay(self.portal)),
            [
                ["admin", ["Owner"], "user", "admin"],
                ["test-user", [u"Reader", u"Reviewer"], "user", u"test_user_1_"],
            ],
        )

    def test_get_local_roles_inherit_roles(self):
        # __ac_local_roles_block__ specifies to block inheritance:
        # https://docs.plone.org/develop/plone/security/local_roles.html
        self.portal.folder1.__ac_local_roles_block__ = True
        transaction.commit()

        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["inherit"], False)

    def test_set_local_roles_inherit(self):
        self.assertEqual(self._get_ac_local_roles_block(self.portal.folder1), False)

        # block local roles
        response = requests.post(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"inherit": False},
        )

        transaction.commit()
        self.assertEqual(self._get_ac_local_roles_block(self.portal.folder1), True)
        # unblock local roles
        response = requests.post(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"inherit": True},
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self._get_ac_local_roles_block(self.portal.folder1), False)

    def test_get_available_roles(self):
        api.user.grant_roles(
            username=TEST_USER_ID, obj=self.portal.folder1, roles=["Reviewer"]
        )
        transaction.commit()

        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIn("available_roles", response)
        self.assertIn(
            {"id": "Reader", "title": "Can view"}, response["available_roles"]
        )

    def test_inherited_global(self):
        api.user.grant_roles(username=TEST_USER_ID, roles=["Reviewer"])
        api.user.grant_roles(
            username=TEST_USER_ID, obj=self.portal.folder1, roles=["Editor"]
        )
        transaction.commit()

        response = requests.get(
            self.portal.folder1.doc1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        response = response.json()
        # find our entry
        entry = [x for x in response["entries"] if x["id"] == TEST_USER_ID][0]

        self.assertEqual("global", entry["roles"]["Reviewer"])
        self.assertEqual("acquired", entry["roles"]["Editor"])

    def test_inherited_global_via_search(self):
        api.user.create(email="jos@henken.local", username="jos")
        api.user.grant_roles(username="jos", roles=["Reviewer"])
        api.user.grant_roles(username="jos", roles=["Editor"], obj=self.portal.folder1)
        transaction.commit()

        response = requests.get(
            self.portal.folder1.doc1.absolute_url() + "/@sharing?search=jos",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        response = response.json()
        # find our entry
        entry = [x for x in response["entries"] if x["id"] == "jos"][0]

        self.assertEqual("global", entry["roles"]["Reviewer"])
        self.assertEqual("acquired", entry["roles"]["Editor"])

    def test_no_serializer_available_returns_501(self):
        # This test unregisters the local_roles adapter. The testrunner can
        # not auto-revert this on test tearDown. Therefore if we ever run
        # into test isolation issues. Start to look here first.
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(SerializeLocalRolesToJson, name="local_roles")

        response = requests.get(
            self.portal.folder1.absolute_url() + "/@sharing",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 501)
        response = response.json()
        self.assertIn("error", response)
        self.assertEqual(u"No serializer available.", response["error"]["message"])

        # we need to re-register the adapter here for following tests
        gsm.registerAdapter(SerializeLocalRolesToJson, name="local_roles")
