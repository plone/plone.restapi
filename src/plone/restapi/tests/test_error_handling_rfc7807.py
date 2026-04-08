from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.problem_types import set_backwards_compat
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import unittest


class TestRFC7807ErrorHandling(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        set_backwards_compat(False)

    def tearDown(self):
        set_backwards_compat(True)
        self.api_session.close()

    def test_login_with_missing_credentials_uses_rfc7807(self):
        response = self.api_session.post("@login", json={"invalid": "data"})

        self.assertEqual(400, response.status_code)
        data = response.json()
        self.assertEqual(data["type"], "/problem-types/validation-error")
        self.assertEqual(data["title"], "Bad Request")
        self.assertEqual(data["status"], 400)
        self.assertIn("detail", data)
        self.assertIn("instance", data)
        self.assertNotIn("error", data)
        self.assertNotIn("message", data)
        self.assertNotIn("error_type", data)
        self.assertNotIn("context", data)
        self.assertNotIn("traceback", data)

    def test_login_with_invalid_credentials_uses_rfc7807(self):
        response = self.api_session.post(
            "@login", json={"login": "invalid", "password": "invalid"}
        )

        self.assertEqual(401, response.status_code)
        data = response.json()
        self.assertEqual(data["type"], "/problem-types/unauthorized")
        self.assertEqual(data["title"], "Unauthorized")
        self.assertEqual(data["status"], 401)
        self.assertEqual(data["detail"], "Wrong login and/or password.")
        self.assertIn("instance", data)
        self.assertNotIn("error", data)
        self.assertNotIn("message", data)
        self.assertNotIn("error_type", data)
        self.assertNotIn("context", data)
        self.assertNotIn("traceback", data)

    def test_unauthorized_response_uses_only_rfc7807_fields(self):
        self.api_session.auth = None
        response = self.api_session.get("@users")

        self.assertEqual(401, response.status_code)
        data = response.json()
        self.assertEqual(data["type"], "/problem-types/unauthorized")
        self.assertEqual(data["title"], "Unauthorized")
        self.assertEqual(data["status"], 401)
        self.assertIn("detail", data)
        self.assertIn("instance", data)
        self.assertEqual(
            set(data.keys()),
            {"type", "title", "status", "detail", "instance"},
        )
