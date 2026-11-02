from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.restapi import form_token
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.MailHost.interfaces import IMailHost
from unittest.mock import patch
from zope.component import getUtility

import os
import transaction
import unittest


class FakeMemcache:
    """The part of pymemcache's HashClient that form_token uses."""

    def __init__(self):
        self.data = {}
        self.working = True

    def set(self, key, value, expire=0, noreply=None):
        if not self.working:
            return False
        self.data[key] = value.encode()
        return True

    def get(self, key):
        return self.data.get(key)

    def delete(self, key, noreply=None):
        return self.data.pop(key, None) is not None


class TestFormToken(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.mailhost = getUtility(IMailHost)

        registry = getUtility(IRegistry)
        registry["plone.email_from_address"] = "info@plone.org"
        registry["plone.email_from_name"] = "Plone test site"

        self.memcache = FakeMemcache()
        self.patches = [
            patch.dict(os.environ, {"FORM_TOKEN_MEMCACHE": "memcached:11211"}),
            patch.object(form_token, "get_client", lambda: self.memcache),
        ]
        for p in self.patches:
            p.start()

        # The visitors who use the contact form are anonymous.
        self.anon_api_session = RelativeSession(self.portal_url, test=self)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        transaction.commit()

    def tearDown(self):
        self.anon_api_session.close()
        for p in self.patches:
            p.stop()

    def get_token(self, age=None):
        """Get a token from @form-token, issued `age` seconds ago."""
        response = self.anon_api_session.get("/@form-token")
        token = response.json()["token"]
        if age is None:
            age = form_token.get_min_age()
        key = form_token.KEY_PREFIX + token
        self.memcache.data[key] = str(int(self.memcache.data[key]) - age).encode()
        return token

    def send(self, token=None):
        data = {"from": "john@doe.com", "message": "Just want to say hi."}
        if token is not None:
            data["form_token"] = token
        response = self.anon_api_session.post("/@email-notification", json=data)
        transaction.commit()
        return response

    def test_form_token(self):
        response = self.anon_api_session.get("/@form-token")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Cache-Control"], "no-store, private")
        data = response.json()
        self.assertEqual(data["min_age"], 15)
        self.assertTrue(form_token.TOKEN_PATTERN.match(data["token"]))
        self.assertIn(form_token.KEY_PREFIX + data["token"], self.memcache.data)

    def test_form_token_memcached_down(self):
        self.memcache.working = False
        response = self.anon_api_session.get("/@form-token")
        self.assertEqual(response.status_code, 503)

    def test_form_token_not_configured(self):
        with patch.dict(os.environ, {"FORM_TOKEN_MEMCACHE": ""}):
            response = self.anon_api_session.get("/@form-token")
        self.assertEqual(response.status_code, 503)

    def test_send_without_token(self):
        response = self.send()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Invalid request.")
        self.assertEqual(self.mailhost.messages, [])

    def test_send_unknown_token(self):
        response = self.send("x" * 43)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Invalid request.")

    def test_send_token_once(self):
        token = self.get_token()
        response = self.send(token)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(self.mailhost.messages), 1)
        response = self.send(token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Invalid request.")

    def test_send_token_too_new(self):
        token = self.get_token(age=form_token.get_min_age() - 2)
        with self.assertLogs(form_token.logger, level="INFO") as logs:
            response = self.send(token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Invalid request.")
        self.assertEqual(
            logs.output,
            [
                "INFO:plone.restapi.form_token:Spam blocked: "
                "reason=early-token form=@email-notification"
            ],
        )
        self.assertEqual(self.mailhost.messages, [])
        # The token is used up: waiting does not help.
        self.assertEqual(self.memcache.data, {})

    def test_min_age_setting(self):
        with patch.dict(os.environ, {"FORM_TOKEN_MIN_AGE": "0"}):
            response = self.send(self.get_token(age=0))
        self.assertEqual(response.status_code, 204)

    def test_send_not_configured(self):
        with patch.dict(os.environ, {"FORM_TOKEN_MEMCACHE": ""}):
            response = self.send()
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(self.mailhost.messages), 1)

    def test_send_pymemcache_not_installed(self):
        with patch.object(form_token, "HashClient", None):
            response = self.send()
        self.assertEqual(response.status_code, 204)

    def test_redeem_rejects_malformed_tokens(self):
        for token in [None, 42, "", "short", "x" * 42 + " ", "x\r\nflush_all\r\n"]:
            self.memcache.data = {form_token.KEY_PREFIX + str(token): b"0"}
            self.assertEqual(form_token.redeem_token(token), form_token.TOKEN_INVALID)
