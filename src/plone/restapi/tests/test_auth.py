from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.permissions import UseRESTAPI
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from unittest import TestCase
from zExceptions import Unauthorized
from zope.event import notify
from ZPublisher.pubevents import PubStart


class TestLogin(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def traverse(self, path="/plone/@login", accept="application/json", method="POST"):
        request = self.layer["request"]
        request.environ["PATH_INFO"] = path
        request.environ["PATH_TRANSLATED"] = path
        request.environ["HTTP_ACCEPT"] = accept
        request.environ["REQUEST_METHOD"] = method
        notify(PubStart(request))
        return request.traverse(path)

    def test_login_without_pas_plugin_fails(self):
        self.portal.acl_users._delOb("jwt_auth")
        service = self.traverse()
        res = service.reply()
        self.assertIn("error", res)
        self.assertNotIn("token", res)

    def test_login_without_credentials_fails(self):
        service = self.traverse()
        res = service.reply()
        self.assertIn("error", res)
        self.assertNotIn("token", res)

    def test_login_with_invalid_credentials_fails(self):
        self.request["BODY"] = '{"login": "admin", "password": "admin"}'
        service = self.traverse()
        res = service.reply()
        self.assertIn("error", res)
        self.assertNotIn("token", res)

    def test_successful_login_returns_token(self):
        self.request["BODY"] = '{{"login": "{}", "password": "{}"}}'.format(
            SITE_OWNER_NAME,
            SITE_OWNER_PASSWORD,
        )
        service = self.traverse()
        res = service.reply()
        self.assertEqual(200, self.request.response.getStatus())
        self.assertIn("token", res)

    def test_invalid_token_returns_400(self):
        invalid_token = "abc123"
        self.request._auth = f"Bearer {invalid_token}"
        self.assertRaises(Unauthorized, self.traverse, path="/plone")

    def test_expired_token_returns_400(self):
        self.portal.acl_users.jwt_auth.store_tokens = True
        token = self.portal.acl_users.jwt_auth.create_token("admin", timeout=-60)
        self.request._auth = f"Bearer {token}"
        self.assertRaises(Unauthorized, self.traverse, path="/plone")

    def test_login_without_api_permission(self):
        self.portal.manage_permission(UseRESTAPI, roles=[])
        self.request["BODY"] = '{{"login": "{}", "password": "{}"}}'.format(
            SITE_OWNER_NAME,
            SITE_OWNER_PASSWORD,
        )
        service = self.traverse()
        res = service.render()
        self.assertIn("token", res)

    def test_login_with_zope_user_fails_without_pas_plugin(self):
        uf = self.layer["app"].acl_users
        uf.plugins.users.addUser("zopeuser", "zopeuser", TEST_USER_PASSWORD)
        if "jwt_auth" in uf:
            uf["jwt_auth"].manage_activateInterfaces([])
        self.request["BODY"] = (
            '{"login": "zopeuser", "password": "' + TEST_USER_PASSWORD + '"}'
        )
        service = self.traverse()
        res = service.reply()
        self.assertIn("error", res)
        self.assertEqual(
            "JWT authentication plugin not installed.", res["error"]["message"]
        )
        self.assertNotIn("token", res)

    def test_login_with_zope_user(self):
        self.layer["app"].acl_users.plugins.users.addUser(
            "zopeuser", "zopeuser", TEST_USER_PASSWORD
        )
        self.request["BODY"] = (
            '{"login": "zopeuser", "password": "' + TEST_USER_PASSWORD + '"}'
        )
        service = self.traverse()
        res = service.reply()
        self.assertEqual(200, self.request.response.getStatus())
        self.assertIn("token", res)


class TestLogout(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def traverse(self, path="/plone/@logout", accept="application/json", method="POST"):
        request = self.layer["request"]
        request.environ["PATH_INFO"] = path
        request.environ["PATH_TRANSLATED"] = path
        request.environ["HTTP_ACCEPT"] = accept
        request.environ["REQUEST_METHOD"] = method
        notify(PubStart(request))
        return request.traverse(path)

    def test_logout_without_pas_plugin_fails(self):
        self.portal.acl_users._delOb("jwt_auth")
        service = self.traverse()
        res = service.reply()
        self.assertIn("error", res)

    def test_logout_with_not_stored_token_just_logouts_user(self):
        self.portal.acl_users.jwt_auth.store_tokens = False
        self.assertEqual(200, self.request.response.getStatus())

    def test_logout_with_without_credentials_fails(self):
        self.portal.acl_users.jwt_auth.store_tokens = True
        service = self.traverse()
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual("Unknown token", res["error"]["message"])

    def test_logout_with_invalid_token_fails(self):
        self.portal.acl_users.jwt_auth.store_tokens = True
        token = "my_invalid_token"
        self.request._auth = f"Bearer {token}"
        service = self.traverse()
        service.reply()
        self.assertEqual(400, self.request.response.getStatus())

    def test_logout_succeeds(self):
        self.portal.acl_users.jwt_auth.store_tokens = True
        token = self.portal.acl_users.jwt_auth.create_token("admin")
        self.request._auth = f"Bearer {token}"
        service = self.traverse()
        service.reply()
        self.assertEqual(200, self.request.response.getStatus())


class TestRenew(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def traverse(
        self, path="/plone/@login-renew", accept="application/json", method="POST"
    ):
        request = self.layer["request"]
        request.environ["PATH_INFO"] = path
        request.environ["PATH_TRANSLATED"] = path
        request.environ["HTTP_ACCEPT"] = accept
        request.environ["REQUEST_METHOD"] = method
        notify(PubStart(request))
        return request.traverse(path)

    def test_renew_without_pas_plugin_fails(self):
        self.portal.acl_users._delOb("jwt_auth")
        service = self.traverse()
        res = service.reply()
        self.assertIn("error", res)

    def test_renew_returns_token(self):
        self.portal.acl_users.jwt_auth.store_tokens = True
        token = self.portal.acl_users.jwt_auth.create_token("admin")
        self.request._auth = f"Bearer {token}"
        service = self.traverse()
        res = service.reply()
        self.assertIn("token", res)

    def test_renew_deletes_old_token(self):
        self.portal.acl_users.jwt_auth.store_tokens = True
        token = self.portal.acl_users.jwt_auth.create_token("admin")
        self.request._auth = f"Bearer {token}"
        service = self.traverse()
        res = service.reply()
        self.assertIn("token", res)
        self.assertEqual(1, len(self.portal.acl_users.jwt_auth._tokens["admin"]))

    def test_renew_fails_on_invalid_token(self):
        token = "this is an invalid token"
        self.request._auth = f"Bearer {token}"
        service = self.traverse()
        res = service.reply()
        self.assertEqual(service.request.response.status, 401)
        self.assertEqual(
            res["error"]["type"], "Invalid or expired authentication token"
        )
