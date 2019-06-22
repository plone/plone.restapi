# -*- coding: utf-8 -*-
from plone.keyring.interfaces import IKeyManager
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

import unittest


class TestJWTAuthenticationPlugin(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):

        self.portal = self.layer["portal"]
        uf = getToolByName(self.portal, "acl_users")
        self.plugin = uf["jwt_auth"]

    def test_challenge(self):
        request = self.layer["request"]
        response = request.response
        self.plugin.challenge(request, request.response)
        self.assertEqual(401, response.getStatus())
        self.assertEqual('Bearer realm="Zope"', response.getHeader("WWW-Authenticate"))

    def test_extract_credentials_without_authorization_header(self):
        request = self.layer["request"]
        request._auth = ""
        self.assertEqual(None, self.plugin.extractCredentials(request))

    def test_extract_credentials_with_other_authorization_header(self):
        request = self.layer["request"]
        request._auth = "Basic YWRtaW46YWRtaW4="
        self.assertEqual(None, self.plugin.extractCredentials(request))

    def test_extract_credentials_with_bearer_authorization_header(self):
        request = self.layer["request"]
        request._auth = (
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9."
            "PGnRccPTXeaxA8nzfytWewWRkizJa_ihI_3H6ec-Zbw"
        )
        self.assertEqual(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiJ9.PGnRccP"
            "TXeaxA8nzfytWewWRkizJa_ihI_3H6ec-Zbw",
            self.plugin.extractCredentials(request)["token"],
        )

    def test_authenticate_credentials_from_unknown_extractor(self):
        creds = {}
        creds["extractor"] = "credentials_basic_auth"
        self.assertEqual(None, self.plugin.authenticateCredentials(creds))

    def test_authenticate_credentials_with_invalid_token(self):
        creds = {}
        creds["extractor"] = "jwt_auth"
        creds["token"] = "invalid"
        self.assertEqual(None, self.plugin.authenticateCredentials(creds))

    def test_authenticate_credentials_without_subject(self):
        creds = {}
        creds["extractor"] = "jwt_auth"
        creds["token"] = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.t-IDcSemACt8x4iTMCda8Yhe"
            "3iZaWbvV5XKSTbuAn0M"
        )
        self.assertEqual(None, self.plugin.authenticateCredentials(creds))

    def test_authenticate_credentials_with_valid_token(self):
        creds = {}
        creds["extractor"] = "jwt_auth"
        creds["token"] = self.plugin.create_token("admin")
        self.assertEqual(("admin", "admin"), self.plugin.authenticateCredentials(creds))

    def test_authenticate_credentials_returns_native_string(self):
        creds = {}
        creds["extractor"] = "jwt_auth"
        creds["token"] = self.plugin.create_token("admin")
        self.assertIsInstance(self.plugin.authenticateCredentials(creds)[0], str)

    def test_decode_token_after_key_rotation(self):
        token = self.plugin.create_token("admin", timeout=0)
        key_manager = getUtility(IKeyManager)
        key_manager.rotate()
        self.assertEqual({"sub": "admin"}, self.plugin._decode_token(token))

    def test_decode_with_static_secret(self):
        self.plugin.use_keyring = False
        token = self.plugin.create_token("admin", timeout=0)
        self.assertEqual({"sub": "admin"}, self.plugin._decode_token(token))

    def test_authenticate_credentials_with_stored_token(self):
        self.plugin.store_tokens = True
        creds = {}
        creds["extractor"] = "jwt_auth"
        creds["token"] = self.plugin.create_token("admin")
        self.assertEqual(("admin", "admin"), self.plugin.authenticateCredentials(creds))

    def test_authenticate_credentials_with_deleted_token_fails(self):
        self.plugin.store_tokens = True
        creds = {}
        creds["extractor"] = "jwt_auth"
        creds["token"] = self.plugin.create_token("admin")
        self.plugin.delete_token(creds["token"])
        self.assertEqual(None, self.plugin.authenticateCredentials(creds))
