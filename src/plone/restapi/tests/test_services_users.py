from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.CMFCore.permissions import SetOwnPassword
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.MailHost.interfaces import IMailHost
from zope.component import getAdapter
from zope.component import getUtility

import transaction
import unittest


class TestUsersEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.mailhost = getUtility(IMailHost)

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.anon_api_session = RelativeSession(self.portal_url)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        properties = {
            "email": "noam.chomsky@example.com",
            "username": "noamchomsky",
            "fullname": "Noam Avram Chomsky",
            "home_page": "web.mit.edu/chomsky",
            "description": "Professor of Linguistics",
            "location": "Cambridge, MA",
        }
        api.user.create(
            email="noam.chomsky@example.com",
            username="noam",
            properties=properties,
            password="password",
        )
        properties = {
            "email": "otheruser@example.com",
            "username": "otheruser",
            "fullname": "Other user",
        }
        api.user.create(
            email="otheruser@example.com",
            username="otheruser",
            properties=properties,
            password="otherpassword",
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()
        self.anon_api_session.close()

    def test_list_users(self):
        response = self.api_session.get("/@users")

        self.assertEqual(200, response.status_code)
        self.assertEqual(4, len(response.json()))
        user_ids = [user["id"] for user in response.json()]
        self.assertIn("admin", user_ids)
        self.assertIn("test_user_1_", user_ids)
        self.assertIn("noam", user_ids)
        noam = [x for x in response.json() if x.get("username") == "noam"][0]
        self.assertEqual("noam", noam.get("id"))
        self.assertEqual(self.portal.absolute_url() + "/@users/noam", noam.get("@id"))
        self.assertEqual("noam.chomsky@example.com", noam.get("email"))
        self.assertEqual("Noam Avram Chomsky", noam.get("fullname"))
        self.assertEqual("web.mit.edu/chomsky", noam.get("home_page"))  # noqa
        self.assertEqual("Professor of Linguistics", noam.get("description"))  # noqa
        self.assertEqual("Cambridge, MA", noam.get("location"))

    def test_list_users_without_being_manager(self):
        noam_api_session = RelativeSession(self.portal_url)
        noam_api_session.headers.update({"Accept": "application/json"})
        noam_api_session.auth = ("noam", "password")

        response = noam_api_session.get("/@users")
        self.assertEqual(response.status_code, 401)
        noam_api_session.close()

    def test_list_users_as_anonymous(self):

        response = self.anon_api_session.get("/@users")
        self.assertEqual(response.status_code, 401)

    def test_add_user(self):
        response = self.api_session.post(
            "/@users",
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "password": "peopleshistory",
                "roles": ["Contributor"],
            },
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        howard = api.user.get(userid="howard")
        self.assertEqual("howard.zinn@example.com", howard.getProperty("email"))
        self.assertIn("Contributor", api.user.get_roles(username="howard"))

    def test_add_user_username_is_required(self):
        response = self.api_session.post("/@users", json={"password": "noamchomsky"})
        transaction.commit()

        self.assertEqual(400, response.status_code)
        self.assertTrue("Property 'username' is required" in response.text)

    def test_add_user_password_is_required(self):
        response = self.api_session.post("/@users", json={"username": "noamchomsky"})
        transaction.commit()

        self.assertEqual(400, response.status_code)
        self.assertTrue(
            ("You have to either send a " "password or sendPasswordReset")
            in response.text
        )

    def test_add_user_email_is_required_if_email_login_is_enabled(self):
        # enable use_email_as_login
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.use_email_as_login = True
        transaction.commit()
        response = self.api_session.post(
            "/@users", json={"username": "noam", "password": "secret"}
        )

        self.assertEqual(400, response.status_code)
        self.assertTrue("Property 'username' is not allowed" in response.text)

    def test_add_user_email_with_email_login_enabled(self):
        # enable use_email_as_login
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.use_email_as_login = True
        transaction.commit()
        response = self.api_session.post(
            "/@users", json={"email": "howard.zinn@example.com", "password": "secret"}
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        self.assertTrue(api.user.get(userid="howard.zinn@example.com"))

    def test_username_is_not_allowed_with_email_login_enabled(self):
        # enable use_email_as_login
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.use_email_as_login = True
        transaction.commit()
        response = self.api_session.post(
            "/@users",
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "password": "secret",
            },
        )
        transaction.commit()

        self.assertEqual(400, response.status_code)
        self.assertTrue("Property 'username' is not allowed" in response.text)

    def test_add_user_with_email_login_enabled(self):
        # enable use_email_as_login
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.use_email_as_login = True
        transaction.commit()
        response = self.api_session.post(
            "/@users", json={"email": "howard.zinn@example.com", "password": "secret"}
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        user = api.user.get(userid="howard.zinn@example.com")
        self.assertTrue(user)
        self.assertEqual("howard.zinn@example.com", user.getUserName())
        self.assertEqual("howard.zinn@example.com", user.getProperty("email"))

    def test_add_user_with_sendPasswordRest_sends_email(self):
        response = self.api_session.post(
            "/@users",
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "sendPasswordReset": True,
            },
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            # Python 3 with Products.MailHost 4.10+
            msg = msg.decode("utf-8")
        self.assertTrue("To: howard.zinn@example.com" in msg)

    def test_add_user_send_properties(self):
        response = self.api_session.post(
            "/@users",
            json={
                "username": "howard",
                "password": "secret",
                "email": "howard.zinn@example.com",
                "fullname": "Howard Zinn",
            },
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        member = api.user.get(username="howard")
        self.assertEqual(member.getProperty("fullname"), "Howard Zinn")

    def test_add_anon_user_sends_properties_are_saved(self):
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.enable_self_reg = True
        transaction.commit()

        response = self.anon_api_session.post(
            "/@users",
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "fullname": "Howard Zinn",
            },
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        member = api.user.get(username="howard")
        self.assertEqual(member.getProperty("fullname"), "Howard Zinn")

    def test_add_anon_no_roles(self):
        """Make sure anonymous users cannot set their own roles.
        Allowing so would make them Manager.
        """
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.enable_self_reg = True
        transaction.commit()

        response = self.anon_api_session.post(
            "/@users",
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "roles": ["Manager"],
            },
        )
        transaction.commit()

        self.assertEqual(400, response.status_code)
        errors = response.json()["error"]["errors"]
        fields = [x["field"] for x in errors]
        self.assertEqual(["roles"], fields)

    def test_add_user_with_uuid_as_userid_enabled(self):
        # enable use_email_as_login
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.use_email_as_login = True
        security_settings.use_uuid_as_userid = True
        transaction.commit()
        response = self.api_session.post(
            "/@users", json={"email": "howard.zinn@example.com", "password": "secret"}
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        user_id = response.json()["id"]
        user = api.user.get(userid=user_id)
        self.assertTrue(user)
        self.assertEqual("howard.zinn@example.com", user.getUserName())
        self.assertEqual("howard.zinn@example.com", user.getProperty("email"))

    def test_get_user(self):
        response = self.api_session.get("/@users/noam")

        self.assertEqual(response.status_code, 200)
        self.assertEqual("noam", response.json().get("id"))
        self.assertEqual(
            self.portal.absolute_url() + "/@users/noam", response.json().get("@id")
        )
        self.assertEqual("noam.chomsky@example.com", response.json().get("email"))
        self.assertEqual("Noam Avram Chomsky", response.json().get("fullname"))
        self.assertEqual(
            "web.mit.edu/chomsky", response.json().get("home_page")
        )  # noqa
        self.assertEqual(
            "Professor of Linguistics", response.json().get("description")
        )  # noqa
        self.assertEqual("Cambridge, MA", response.json().get("location"))

    def test_get_user_as_anonymous(self):
        response = self.anon_api_session.get("/@users/noam")
        self.assertEqual(response.status_code, 401)

    def test_get_other_user_info_when_logged_in(self):
        noam_api_session = RelativeSession(self.portal_url)
        noam_api_session.headers.update({"Accept": "application/json"})
        noam_api_session.auth = ("noam", "password")

        response = noam_api_session.get("/@users/otheruser")
        self.assertEqual(response.status_code, 401)
        noam_api_session.close()

    def test_get_search_user_with_filter(self):
        response = self.api_session.post(
            "/@users",
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "password": "peopleshistory",
            },
        )
        transaction.commit()
        response = self.api_session.get("/@users", params={"query": "noa"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual("noam", response.json()[0].get("id"))
        self.assertEqual(
            self.portal.absolute_url() + "/@users/noam", response.json()[0].get("@id")
        )
        self.assertEqual("noam.chomsky@example.com", response.json()[0].get("email"))
        self.assertEqual(
            "Noam Avram Chomsky", response.json()[0].get("fullname")
        )  # noqa

        response = self.api_session.get("/@users", params={"query": "howa"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual("howard", response.json()[0].get("id"))

    def test_get_search_user_with_filter_as_anonymous(self):
        response = self.api_session.post(
            "/@users",
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "password": "peopleshistory",
            },
        )
        transaction.commit()
        response = self.anon_api_session.get("/@users", params={"query": "howa"})
        self.assertEqual(response.status_code, 401)

    def test_get_search_user_with_filter_as_unauthorized_user(self):
        response = self.api_session.post(
            "/@users",
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "password": "peopleshistory",
            },
        )
        transaction.commit()
        noam_api_session = RelativeSession(self.portal_url)
        noam_api_session.headers.update({"Accept": "application/json"})
        noam_api_session.auth = ("noam", "password")

        response = noam_api_session.get("/@users", params={"query": "howa"})
        self.assertEqual(response.status_code, 401)
        noam_api_session.close()

    def test_get_non_existing_user(self):
        response = self.api_session.get("/@users/non-existing-user")

        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        payload = {
            "fullname": "Noam A. Chomsky",
            "username": "avram",
            "email": "avram.chomsky@example.com",
        }
        response = self.api_session.patch("/@users/noam", json=payload)
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        noam = api.user.get(userid="noam")
        self.assertEqual("noam", noam.getUserId())  # user id never changes
        self.assertEqual("avram", noam.getUserName())
        self.assertEqual("Noam A. Chomsky", noam.getProperty("fullname"))
        self.assertEqual("avram.chomsky@example.com", noam.getProperty("email"))

    def test_user_can_update_himself(self):
        payload = {
            "fullname": "Noam A. Chomsky",
            "username": "noam",
            "email": "avram.chomsky@plone.org",
        }
        self.api_session.auth = ("noam", "password")
        response = self.api_session.patch("/@users/noam", json=payload)

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        noam = api.user.get(userid="noam")
        self.assertEqual("noam", noam.getUserId())  # user id never changes
        self.assertEqual("Noam A. Chomsky", noam.getProperty("fullname"))
        self.assertEqual("avram.chomsky@plone.org", noam.getProperty("email"))

    def test_user_can_update_himself_remove_values(self):
        payload = {
            "fullname": "Noam A. Chomsky",
            "username": "noam",
            "email": "avram.chomsky@plone.org",
            "home_page": None,
        }
        self.api_session.auth = ("noam", "password")
        response = self.api_session.patch("/@users/noam", json=payload)

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        noam = api.user.get(userid="noam")

        self.assertEqual(None, noam.getProperty("home_page"))

    def test_update_roles(self):
        self.assertNotIn("Contributor", api.user.get_roles(username="noam"))

        self.api_session.patch("/@users/noam", json={"roles": {"Contributor": True}})
        transaction.commit()
        self.assertIn("Contributor", api.user.get_roles(username="noam"))

        self.api_session.patch("/@users/noam", json={"roles": {"Contributor": False}})
        transaction.commit()
        self.assertNotIn("Contributor", api.user.get_roles(username="noam"))

    def test_update_user_password(self):
        old_password_hashes = dict(self.portal.acl_users.source_users._user_passwords)
        payload = {"password": "secret"}
        response = self.api_session.patch("/@users/noam", json=payload)
        transaction.commit()

        self.assertEqual(response.status_code, 204)

        new_password_hashes = dict(self.portal.acl_users.source_users._user_passwords)
        self.assertNotEqual(old_password_hashes["noam"], new_password_hashes["noam"])

    def test_update_portrait(self):
        payload = {
            "portrait": {
                "filename": "image.gif",
                "encoding": "base64",
                "data": "R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=",
                "content-type": "image/gif",
            }
        }
        self.api_session.auth = ("noam", "password")
        response = self.api_session.patch("/@users/noam", json=payload)

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        user = self.api_session.get("/@users/noam").json()
        self.assertTrue(
            user.get("portrait").endswith("plone/portal_memberdata/portraits/noam")
        )

    def test_update_portrait_with_default_plone_scaling(self):
        payload = {
            "portrait": {
                "filename": "image.gif",
                "encoding": "base64",
                "data": "R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=",
                "content-type": "image/gif",
                "scale": True,
            }
        }
        self.api_session.auth = ("noam", "password")
        response = self.api_session.patch("/@users/noam", json=payload)

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        user = self.api_session.get("/@users/noam").json()
        self.assertTrue(
            user.get("portrait").endswith("plone/portal_memberdata/portraits/noam")
        )

    def test_update_portrait_by_manager(self):
        payload = {
            "portrait": {
                "filename": "image.gif",
                "encoding": "base64",
                "data": "R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=",
                "content-type": "image/gif",
            }
        }
        response = self.api_session.patch("/@users/noam", json=payload)

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        user = self.api_session.get("/@users/noam").json()
        self.assertTrue(
            user.get("portrait").endswith("plone/portal_memberdata/portraits/noam")
        )

    def test_delete_portrait(self):
        payload = {
            "portrait": None,
        }
        self.api_session.auth = ("noam", "password")
        response = self.api_session.patch("/@users/noam", json=payload)

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        user = self.api_session.get("/@users/noam").json()

        self.assertTrue(user.get("portrait") is None)

    def test_delete_portrait_by_manager(self):
        payload = {
            "portrait": None,
        }
        response = self.api_session.patch("/@users/noam", json=payload)

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        user = self.api_session.get("/@users/noam").json()

        self.assertTrue(user.get("portrait") is None)

    def test_update_user_with_portrait_set_without_updating_portrait(self):
        payload = {
            "portrait": {
                "filename": "image.gif",
                "encoding": "base64",
                "data": "R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=",
                "content-type": "image/gif",
            }
        }
        self.api_session.auth = ("noam", "password")
        response = self.api_session.patch("/@users/noam", json=payload)

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        payload = {
            "fullname": "Noam A. Chomsky",
            "username": "noam",
            "email": "avram.chomsky@plone.org",
            "portrait": "http://localhost:55001/plone/portal_memberdata/portraits/noam",
        }
        self.api_session.auth = ("noam", "password")
        response = self.api_session.patch("/@users/noam", json=payload)

        self.assertEqual(response.status_code, 204)
        transaction.commit()

        user = self.api_session.get("/@users/noam").json()
        self.assertTrue(
            user.get("portrait").endswith("plone/portal_memberdata/portraits/noam")
        )

    def test_anonymous_user_can_not_update_existing_user(self):
        payload = {
            "fullname": "Noam A. Chomsky",
            "username": "noam",
            "email": "avram.chomsky@plone.org",
        }
        self.api_session.auth = ("noam", "password")
        response = self.anon_api_session.patch("/@users/noam", json=payload)

        self.assertEqual(response.status_code, 401)

    def test_user_can_not_update_another_user(self):
        payload = {
            "fullname": "Noam A. Chomsky",
            "username": "noam",
            "email": "avram.chomsky@plone.org",
        }
        self.api_session.auth = ("otheruser", "otherpassword")
        response = self.api_session.patch("/@users/noam", json=payload)

        self.assertEqual(response.status_code, 403)

    def test_user_requests_password_sends_password_via_mail(self):
        self.api_session.auth = ("noam", "password")
        payload = {}
        response = self.api_session.post("/@users/noam/reset-password", json=payload)
        transaction.commit()

        self.assertEqual(response.status_code, 200)
        # FIXME: Test that mail is sent

    def test_user_can_set_her_own_password(self):
        self.api_session.auth = ("noam", "password")
        self.portal.manage_permission(
            SetOwnPassword, roles=["Authenticated", "Manager"], acquire=False
        )
        transaction.commit()

        payload = {"old_password": "password", "new_password": "new_password"}
        response = self.api_session.post("/@users/noam/reset-password", json=payload)
        transaction.commit()

        self.assertEqual(response.status_code, 200)
        authed = self.portal.acl_users.authenticate("noam", "new_password", {})
        self.assertTrue(authed)

    def test_normal_authenticated_user_cannot_set_other_users_password(self):
        self.api_session.auth = ("noam", "password")
        self.portal.manage_permission(
            SetOwnPassword, roles=["Authenticated", "Manager"], acquire=False
        )
        transaction.commit()

        payload = {"old_password": "password", "new_password": "new_password"}
        response = self.api_session.post(
            "/@users/otheruser/reset-password", json=payload
        )
        transaction.commit()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["type"], "Wrong user")

    def test_user_set_own_password_requires_set_own_password_permission(self):
        self.api_session.auth = ("noam", "password")
        self.portal.manage_permission(SetOwnPassword, roles=["Manager"], acquire=False)
        transaction.commit()

        payload = {"old_password": "password", "new_password": "new_password"}
        response = self.api_session.post("/@users/noam/reset-password", json=payload)
        transaction.commit()

        self.assertEqual(response.status_code, 403)

    def test_user_set_own_password_requires_old_and_new_password(self):
        self.api_session.auth = ("noam", "password")
        payload = {"old_password": "password"}
        response = self.api_session.post("/@users/noam/reset-password", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["type"], "Invalid parameters")
        payload = {"new_password": "new_password"}
        response = self.api_session.post("/@users/noam/reset-password", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["type"], "Invalid parameters")

    def test_user_set_own_password_checks_old_password(self):
        self.api_session.auth = ("noam", "password")
        payload = {"new_password": "new_password", "old_password": "wrong_password"}
        response = self.api_session.post("/@users/noam/reset-password", json=payload)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["type"], "Wrong password")

    def test_user_set_reset_token_requires_new_password(self):
        self.api_session.auth = ("noam", "password")
        payload = {"reset_token": "abc"}
        response = self.api_session.post("/@users/noam/reset-password", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["type"], "Invalid parameters")

    def test_reset_with_token(self):
        reset_tool = getToolByName(self.portal, "portal_password_reset")
        reset_info = reset_tool.requestReset("noam")
        token = reset_info["randomstring"]
        transaction.commit()

        payload = {"reset_token": token, "new_password": "new_password"}
        response = self.api_session.post("/@users/noam/reset-password", json=payload)
        transaction.commit()

        self.assertEqual(response.status_code, 200)
        authed = self.portal.acl_users.authenticate("noam", "new_password", {})
        self.assertTrue(authed)

    def test_reset_with_uuid_as_userid_and_login_email_using_id(self):
        # enable use_email_as_login
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.use_email_as_login = True
        security_settings.use_uuid_as_userid = True
        transaction.commit()

        response = self.api_session.post(
            "/@users", json={"email": "howard.zinn@example.com", "password": "secret"}
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        user_id = response.json()["id"]
        user = api.user.get(userid=user_id)
        self.assertTrue(user)

        reset_tool = getToolByName(self.portal, "portal_password_reset")
        reset_info = reset_tool.requestReset(user.id)
        token = reset_info["randomstring"]
        transaction.commit()

        payload = {"reset_token": token, "new_password": "new_password"}
        response = self.api_session.post(
            f"/@users/{user.id}/reset-password", json=payload
        )

        self.assertEqual(response.status_code, 200)

    def test_reset_with_uuid_as_userid_and_login_email_using_mail(self):
        # enable use_email_as_login
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.use_email_as_login = True
        security_settings.use_uuid_as_userid = True
        transaction.commit()

        response = self.api_session.post(
            "/@users", json={"email": "howard.zinn@example.com", "password": "secret"}
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        user_id = response.json()["id"]
        user = api.user.get(userid=user_id)
        self.assertTrue(user)

        reset_tool = getToolByName(self.portal, "portal_password_reset")
        reset_info = reset_tool.requestReset(user.id)
        token = reset_info["randomstring"]
        transaction.commit()

        payload = {"reset_token": token, "new_password": "new_password"}
        response = self.api_session.post(
            f"/@users/{user.getUserName()}/reset-password", json=payload
        )

        self.assertEqual(response.status_code, 200)

    def test_reset_and_login_email_using_mail(self):
        # enable use_email_as_login
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.use_email_as_login = True
        transaction.commit()

        response = self.api_session.post(
            "/@users", json={"email": "howard.zinn@example.com", "password": "secret"}
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        user_id = response.json()["id"]
        user = api.user.get(userid=user_id)
        self.assertTrue(user)

        reset_tool = getToolByName(self.portal, "portal_password_reset")
        reset_info = reset_tool.requestReset(user.id)
        token = reset_info["randomstring"]
        transaction.commit()

        payload = {"reset_token": token, "new_password": "new_password"}
        response = self.api_session.post(
            f"/@users/{user.getUserName()}/reset-password", json=payload
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        response = self.api_session.delete("/@users/noam")
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(None, api.user.get(userid="noam"))

    def test_delete_non_existing_user(self):
        response = self.api_session.delete("/@users/non-existing-user")
        transaction.commit()

        self.assertEqual(response.status_code, 404)

    def test_anonymous_requires_enable_self_reg(self):
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.enable_self_reg = False
        transaction.commit()

        response = self.anon_api_session.post(
            "/@users", json={"password": "noamchomsky"}
        )
        transaction.commit()

        self.assertEqual(403, response.status_code)

        security_settings.enable_self_reg = True
        transaction.commit()

        response = self.anon_api_session.post(
            "/@users",
            json={"username": "new_user", "email": "avram.chomsky@example.com"},
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)

    def test_anonymous_without_enable_user_pwd_choice_sends_mail(self):
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.enable_self_reg = True
        transaction.commit()

        response = self.anon_api_session.post(
            "/@users",
            json={"username": "new_user", "email": "avram.chomsky@example.com"},
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            # Python 3 with Products.MailHost 4.10+
            msg = msg.decode("utf-8")
        self.assertTrue("To: avram.chomsky@example.com" in msg)

    def test_anonymous_can_set_password_with_enable_user_pwd_choice(self):
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.enable_self_reg = True
        transaction.commit()

        response = self.anon_api_session.post(
            "/@users",
            json={
                "username": "new_user",
                "email": "avram.chomsky@example.com",
                "password": "secret",
            },
        )
        transaction.commit()

        self.assertEqual(400, response.status_code)
        self.assertTrue("Property 'password' is not allowed" in response.text)

        security_settings.enable_user_pwd_choice = True
        transaction.commit()

        response = self.anon_api_session.post(
            "/@users",
            json={
                "username": "new_user",
                "email": "avram.chomsky@example.com",
                "password": "secret",
            },
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)

    def test_anonymous_with_enable_user_pwd_choice_doent_send_email(self):
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.enable_self_reg = True
        security_settings.enable_user_pwd_choice = True
        transaction.commit()

        response = self.anon_api_session.post(
            "/@users",
            json={
                "username": "new_user",
                "email": "avram.chomsky@example.com",
                "password": "secret",
            },
        )
        transaction.commit()

        self.assertEqual(self.mailhost.messages, [])
        self.assertEqual(201, response.status_code)

    def test_anonymous_with_enable_user_sets_only_member_role(self):
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.enable_self_reg = True
        security_settings.enable_user_pwd_choice = True
        transaction.commit()

        response = self.anon_api_session.post(
            "/@users",
            json={
                "username": "new_user",
                "email": "avram.chomsky@example.com",
                "password": "secret",
            },
        )

        response = response.json()
        self.assertIn("Member", response["roles"])
        self.assertEqual(1, len(response["roles"]))

    def test_add_user_no_roles_sets_member_as_sensible_default(self):
        response = self.api_session.post(
            "/@users",
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "password": "peopleshistory",
            },
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)

        response = response.json()

        self.assertIn("Member", response["roles"])
        self.assertEqual(1, len(response["roles"]))
