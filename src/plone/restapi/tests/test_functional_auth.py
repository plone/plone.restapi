from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

import base64
import requests
import transaction
import unittest


class TestFunctionalAuth(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, SITE_OWNER_NAME)
        self.private_document = self.portal[
            self.portal.invokeFactory("Document", id="doc1", title="My Document")
        ]
        self.private_document_url = self.private_document.absolute_url()
        transaction.commit()

    def test_login_without_credentials_fails(self):
        response = requests.post(
            self.portal_url + "/@login", headers={"Accept": "application/json"}
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            "Missing credentials", response.json().get("error").get("type")
        )
        self.assertEqual(
            "Login and password must be provided in body.",
            response.json().get("error").get("message"),
        )

    def test_login_with_invalid_credentials_fails(self):
        response = requests.post(
            self.portal_url + "/@login",
            headers={"Accept": "application/json"},
            json={"login": "invalid", "password": "invalid"},
        )
        self.assertEqual(401, response.status_code)
        self.assertEqual(
            "Invalid credentials", response.json().get("error").get("type")
        )
        self.assertEqual(
            "Wrong login and/or password.", response.json().get("error").get("message")
        )

    def test_login_with_valid_credentials_returns_token(self):
        response = requests.post(
            self.portal_url + "/@login",
            headers={"Accept": "application/json"},
            json={"login": TEST_USER_NAME, "password": TEST_USER_PASSWORD},
        )
        self.assertEqual(200, response.status_code)
        self.assertIn("token", response.json())

    def test_api_login_grants_zmi(self):
        """
        Logging in via the API also grants access to the Zope root ZMI.
        """
        session = requests.Session()
        self.addCleanup(session.close)
        login_resp = session.post(
            self.portal_url + "/@login",
            headers={"Accept": "application/json"},
            json={"login": SITE_OWNER_NAME, "password": TEST_USER_PASSWORD},
        )
        self.assertIn(
            "__ac",
            login_resp.cookies,
            "Plone session cookie missing from API login POST response",
        )
        self.assertEqual(
            login_resp.status_code,
            200,
            "Wrong API login response status code",
        )
        self.assertIn(
            "token",
            login_resp.json(),
            "Authentication token missing from API response JSON",
        )

        zmi_resp = session.get(
            self.layer["app"].absolute_url() + "/manage_workspace",
        )
        # Works in the browser when running `$ bin/instance fg` in a `plone.restapi`
        # checkout against `http://localhost:8080/manage_main` but doesn't work in the
        # browser against the test fixture at `http://localhost:55001/manage_main`.  My
        # guess is that there's some subtle difference in the PAS plugin configuration.
        self.skipTest("FIXME: Works in real instance but not test fixture")
        self.assertEqual(
            zmi_resp.status_code,
            200,
            "Wrong ZMI view response status code",
        )
        self.assertTrue(
            '<a href="plone/manage_workspace">' in zmi_resp.text,
            "Wrong ZMI view response content",
        )

    def test_zmi_login_grants_api(self):
        """
        Logging in via the Zope root ZMI also grants access to the API.
        """
        session = requests.Session()
        self.addCleanup(session.close)
        basic_auth_headers = {
            "Authorization": "Basic {}".format(
                base64.b64encode(
                    f"{SITE_OWNER_NAME}:{TEST_USER_PASSWORD}".encode(),
                ).decode()
            )
        }
        zmi_resp = session.get(
            self.layer["app"].absolute_url() + "/manage_workspace",
            headers=basic_auth_headers,
        )
        self.assertEqual(
            zmi_resp.status_code,
            200,
            "Wrong ZMI login response status code",
        )
        self.assertTrue(
            '<a href="plone/manage_workspace">' in zmi_resp.text,
            "Wrong ZMI view response content",
        )

        api_basic_auth_headers = dict(basic_auth_headers)
        api_basic_auth_headers["Accept"] = "application/json"
        api_resp = session.get(
            self.private_document_url,
            headers=api_basic_auth_headers,
        )
        self.assertEqual(
            api_resp.status_code,
            200,
            "Wrong API view response status code",
        )
        api_json = api_resp.json()
        self.assertIn(
            "@id",
            api_json,
            "Plone object id missing from API response JSON",
        )
        self.assertEqual(
            api_json["@id"],
            self.private_document_url,
            "Wrong Plone object URL from API response JSON",
        )

    def test_cookie_login_grants_api(self):
        """
        Logging in via the Plone login form also grants access to the API.
        """
        session = requests.Session()
        self.addCleanup(session.close)
        challenge_resp = session.get(self.private_document_url)
        self.assertEqual(
            challenge_resp.status_code,
            200,
            "Wrong Plone login challenge status code",
        )
        self.assertTrue(
            '<input id="__ac_password" name="__ac_password"' in challenge_resp.text,
            "Plone login challenge response content missing password field",
        )
        login_resp = session.post(
            self.portal_url + "/login",
            data={
                "__ac_name": SITE_OWNER_NAME,
                "__ac_password": TEST_USER_PASSWORD,
                "came_from": "/".join(self.private_document.getPhysicalPath()),
                "buttons.login": "Log in",
            },
        )
        self.assertIn(
            "__ac",
            login_resp.history[0].cookies,
            "Plone session cookie missing form login POST response",
        )
        self.assertEqual(
            login_resp.status_code,
            200,
            "Wrong Plone login response status code",
        )
        self.assertEqual(
            login_resp.url,
            self.private_document_url,
            "Plone login response didn't redirect to original URL",
        )

        api_resp = session.get(
            self.private_document_url,
            headers={"Accept": "application/json"},
        )
        self.assertEqual(
            api_resp.status_code,
            200,
            "Wrong API view response status code",
        )
        api_json = api_resp.json()
        self.assertIn(
            "@id",
            api_json,
            "Plone object id missing from API response JSON",
        )
        self.assertEqual(
            api_json["@id"],
            self.private_document_url,
            "Wrong Plone object URL from API response JSON",
        )

    def test_accessing_private_document_with_valid_token_succeeds(self):
        # login and generate a valid token
        response = requests.post(
            self.portal_url + "/@login",
            headers={"Accept": "application/json"},
            json={"login": TEST_USER_NAME, "password": TEST_USER_PASSWORD},
        )
        valid_token = response.json().get("token")

        # use valid token to access a private resource
        response = requests.get(
            self.private_document_url,
            headers={
                "Accept": "application/json",
                "Authorization": "Bearer " + valid_token,
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue("@id" in response.json())

    def test_accessing_private_document_with_invalid_token_fails(self):
        invalid_token = "abcd1234"
        response = requests.get(
            self.private_document_url,
            headers={
                "Accept": "application/json",
                "Authorization": "Bearer " + invalid_token,
            },
        )

        self.assertEqual(401, response.status_code)
        self.assertEqual("Unauthorized", response.json().get("type"))
        self.assertEqual(
            "You are not authorized to access this resource.",
            response.json().get("message"),
        )

    def test_accessing_private_document_with_expired_token_fails(self):
        # generate an expired token
        self.portal.acl_users.jwt_auth.store_tokens = True
        expired_token = self.portal.acl_users.jwt_auth.create_token(
            "admin", timeout=-60
        )
        transaction.commit()

        response = requests.get(
            self.private_document_url,
            headers={
                "Accept": "application/json",
                "Authorization": "Bearer " + expired_token,
            },
        )

        self.assertEqual(401, response.status_code)
        self.assertEqual("Unauthorized", response.json().get("type"))
        self.assertEqual(
            "You are not authorized to access this resource.",
            response.json().get("message"),
        )
