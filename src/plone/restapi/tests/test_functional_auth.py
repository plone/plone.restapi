# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

import requests
import transaction
import unittest


class TestFunctionalAuth(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, SITE_OWNER_NAME)
        self.private_document = self.portal[self.portal.invokeFactory(
            'Document',
            id='doc1',
            title='My Document'
        )]
        self.private_document_url = self.private_document.absolute_url()
        transaction.commit()

    def test_login_without_credentials_fails(self):
        response = requests.post(
            self.portal_url + '/@login',
            headers={'Accept': 'application/json'},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            u'Missing credentials',
            response.json().get('error').get('type')
        )
        self.assertEqual(
            u'Login and password must be provided in body.',
            response.json().get('error').get('message')
        )

    def test_login_with_invalid_credentials_fails(self):
        response = requests.post(
            self.portal_url + '/@login',
            headers={'Accept': 'application/json'},
            json={
                "login": "invalid",
                "password": "invalid",
            },
        )
        self.assertEqual(401, response.status_code)
        self.assertEqual(
            u'Invalid credentials',
            response.json().get('error').get('type')
        )
        self.assertEqual(
            u'Wrong login and/or password.',
            response.json().get('error').get('message')
        )

    def test_login_with_valid_credentials_returns_token(self):
        response = requests.post(
            self.portal_url + '/@login',
            headers={'Accept': 'application/json'},
            json={
                "login": TEST_USER_NAME,
                "password": TEST_USER_PASSWORD,
            },
        )
        self.assertEqual(200, response.status_code)
        self.assertTrue(
            u'token' in response.json()
        )

    def test_accessing_private_document_with_valid_token_succeeds(self):
        # login and generate a valid token
        response = requests.post(
            self.portal_url + '/@login',
            headers={'Accept': 'application/json'},
            json={
                "login": TEST_USER_NAME,
                "password": TEST_USER_PASSWORD,
            },
        )
        valid_token = response.json().get('token')

        # use valid token to access a private resource
        response = requests.get(
            self.private_document_url,
            headers={
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + valid_token
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(u'@id' in response.json())

    def test_accessing_private_document_with_invalid_token_fails(self):
        invalid_token = 'abcd1234'
        response = requests.get(
            self.private_document_url,
            headers={
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + invalid_token
            },
        )

        self.assertEqual(401, response.status_code)
        self.assertEqual(
            u'Unauthorized',
            response.json().get('type')
        )
        self.assertEqual(
            u'You are not authorized to access this resource.',
            response.json().get('message')
        )

    def test_accessing_private_document_with_expired_token_fails(self):
        # generate an expired token
        self.portal.acl_users.jwt_auth.store_tokens = True
        expired_token = self.portal.acl_users.jwt_auth.create_token(
            'admin',
            timeout=-60
        )
        transaction.commit()

        response = requests.get(
            self.private_document_url,
            headers={
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + expired_token
            },
        )

        self.assertEqual(401, response.status_code)
        self.assertEqual(
            u'Unauthorized',
            response.json().get('type')
        )
        self.assertEqual(
            u'You are not authorized to access this resource.',
            response.json().get('message')
        )
