from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestGroupsEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.gtool = api.portal.get_tool("portal_groups")
        properties = {
            "title": "Plone Team",
            "description": "We are Plone",
            "email": "ploneteam@plone.org",
        }
        self.gtool.addGroup(
            "ploneteam",
            (),
            (),
            properties=properties,
            title=properties["title"],
            description=properties["description"],
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def set_siteadm(self):
        siteadm_username = "siteadm"
        siteadm_password = "siteadmpassword"
        api.user.create(
            email="siteadm@example.com",
            roles=["Site Administrator"],
            username=siteadm_username,
            password=siteadm_password,
        )
        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (siteadm_username, siteadm_password)
        transaction.commit()

    def test_list_groups(self):
        response = self.api_session.get("/@groups")

        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.json()))
        user_ids = [group["id"] for group in response.json()]
        self.assertIn("Administrators", user_ids)
        self.assertIn("Reviewers", user_ids)
        self.assertIn("AuthenticatedUsers", user_ids)
        self.assertIn("ploneteam", user_ids)
        ptgroup = [x for x in response.json() if x.get("groupname") == "ploneteam"][0]
        self.assertEqual("ploneteam", ptgroup.get("id"))
        self.assertEqual(
            self.portal.absolute_url() + "/@groups/ploneteam", ptgroup.get("@id")
        )
        self.assertEqual("ploneteam@plone.org", ptgroup.get("email"))
        self.assertEqual("Plone Team", ptgroup.get("title"))
        self.assertEqual("We are Plone", ptgroup.get("description"))

        self.assertEqual(ptgroup.get("roles"), ["Authenticated"])

        # # Assert batched list of group members
        self.assertTrue(
            all(["members" in group for group in response.json()]),
            "Members key found in groups listing",
        )

    def test_add_group(self):
        response = self.api_session.post(
            "/@groups",
            json={
                "groupname": "fwt",
                "email": "fwt@plone.org",
                "title": "Framework Team",
                "description": "The Plone Framework Team",
                "roles": ["Manager"],
                "groups": ["Administrators"],
                "users": [SITE_OWNER_NAME, TEST_USER_ID],
            },
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        fwt = self.gtool.getGroupById("fwt")
        self.assertEqual("fwt@plone.org", fwt.getProperty("email"))
        self.assertTrue(
            {SITE_OWNER_NAME, TEST_USER_ID}.issubset(set(fwt.getGroupMemberIds())),
            "Userids not found in group",
        )

    def test_add_group_groupname_is_required(self):
        response = self.api_session.post("/@groups", json={"title": "Framework Team"})
        transaction.commit()

        self.assertEqual(400, response.status_code)
        self.assertTrue("\"Property 'groupname' is required" in response.text)

    def test_get_group(self):
        response = self.api_session.get("/@groups/ploneteam")

        self.assertEqual(response.status_code, 200)
        self.assertEqual("ploneteam", response.json().get("id"))
        self.assertEqual(
            self.portal.absolute_url() + "/@groups/ploneteam",
            response.json().get("@id"),
        )
        self.assertEqual("ploneteam@plone.org", response.json().get("email"))
        self.assertEqual("ploneteam@plone.org", response.json().get("email"))
        self.assertEqual("Plone Team", response.json().get("title"))
        self.assertEqual("We are Plone", response.json().get("description"))
        self.assertIn("members", response.json())

    def test_get_search_group_with_filter(self):
        response = self.api_session.get("/@groups", params={"query": "plo"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual("ploneteam", response.json()[0].get("id"))
        self.assertEqual(
            self.portal.absolute_url() + "/@groups/ploneteam",
            response.json()[0].get("@id"),
        )
        self.assertEqual("ploneteam@plone.org", response.json()[0].get("email"))

        response = self.api_session.get("/@groups", params={"query": "Auth"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual("AuthenticatedUsers", response.json()[0].get("id"))

    def test_get_non_existing_group(self):
        response = self.api_session.get("/@groups/non-existing-group")

        self.assertEqual(response.status_code, 404)

    def test_update_group(self):
        ploneteam = self.gtool.getGroupById("ploneteam")
        ploneteam.addMember(SITE_OWNER_NAME)
        transaction.commit()
        self.assertNotIn(TEST_USER_ID, ploneteam.getGroupMemberIds())
        self.assertIn(SITE_OWNER_NAME, ploneteam.getGroupMemberIds())

        payload = {
            "groupname": "ploneteam",
            "email": "ploneteam2@plone.org",
            "users": {TEST_USER_ID: True, SITE_OWNER_NAME: False},
        }
        response = self.api_session.patch("/@groups/ploneteam", json=payload)
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        ploneteam = self.gtool.getGroupById("ploneteam")
        self.assertEqual("ploneteam", ploneteam.id)
        self.assertEqual("Plone Team", ploneteam.getProperty("title"))
        self.assertEqual("ploneteam2@plone.org", ploneteam.getProperty("email"))
        self.assertIn(TEST_USER_ID, ploneteam.getGroupMemberIds())
        self.assertNotIn(SITE_OWNER_NAME, ploneteam.getGroupMemberIds())

    def test_delete_group(self):
        response = self.api_session.delete("/@groups/ploneteam")
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(None, self.gtool.getGroupById("ploneteam"))

    def test_delete_non_existing_group(self):
        response = self.api_session.delete("/@groups/non-existing-group")
        transaction.commit()

        self.assertEqual(response.status_code, 404)

    def test_siteadm_add_user_to_group(self):
        self.set_siteadm()
        payload = {
            "users": {TEST_USER_ID: True, SITE_OWNER_NAME: False},
        }
        self.api_session.patch("/@groups/Reviewers", json=payload)
        transaction.commit()

        reviewers = self.gtool.getGroupById("Reviewers")
        self.assertIn(TEST_USER_ID, reviewers.getGroupMemberIds())

    def test_siteadm_not_add_user_to_group_with_manager_role(self):
        self.set_siteadm()
        payload = {
            "users": {TEST_USER_ID: True, SITE_OWNER_NAME: False},
        }
        self.api_session.patch("/@groups/Administrators", json=payload)
        transaction.commit()

        administrators = self.gtool.getGroupById("Administrators")
        self.assertNotIn(TEST_USER_ID, administrators.getGroupMemberIds())

    def test_siteadm_not_add_group_to_group_with_manager_role(self):
        self.set_siteadm()
        transaction.commit()

        payload = {
            "groups": ["Administrators"],
        }
        self.api_session.patch("/@groups/ploneteam", json=payload)
        transaction.commit()

        administrators = self.gtool.getGroupById("Administrators")
        self.assertNotIn("ploneteam", administrators.getGroupMemberIds())

    def test_siteadm_not_set_manager_to_group(self):
        self.set_siteadm()
        payload = {
            "roles": ["Manager"],
        }
        self.api_session.patch("/@groups/ploneteam", json=payload)
        transaction.commit()

        ploneteam = self.gtool.getGroupById("ploneteam")
        self.assertNotIn("Manager", ploneteam.getRoles())

    def test_siteadm_not_add_group_with_manager_role(self):
        self.set_siteadm()
        self.api_session.post(
            "/@groups",
            json={
                "groupname": "fwt",
                "roles": ["Manager"],
            },
        )
        transaction.commit()

        fwt = self.gtool.getGroupById("fwt")
        self.assertIsNone(fwt)

    def test_siteadm_not_delete_group_with_manager_role(self):
        self.set_siteadm()
        self.api_session.delete("/@groups/Administrators")
        transaction.commit()

        self.assertIsNotNone(self.gtool.getGroupById("Administrators"))
