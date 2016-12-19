# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getAdapter

try:
    from Products.CMFPlone.interfaces import ISecuritySchema
except ImportError:
    from plone.app.controlpanel.security import ISecuritySchema

import transaction
import unittest


class TestUsersEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        properties = {
            'email': 'noam.chomsky@example.com',
            'username': 'noamchomsky',
            'fullname': 'Noam Avram Chomsky',
            'home_page': 'web.mit.edu/chomsky',
            'description': 'Professor of Linguistics',
            'location': 'Cambridge, MA'
        }
        api.user.create(
            email='noam.chomsky@example.com',
            username='noam',
            properties=properties
        )
        transaction.commit()

    def test_list_users(self):
        response = self.api_session.get('/@users')

        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.json()))
        user_ids = [user['id'] for user in response.json()]
        self.assertIn('admin', user_ids)
        self.assertIn('test_user_1_', user_ids)
        self.assertIn('noam', user_ids)
        noam = [x for x in response.json() if x.get('username') == 'noam'][0]
        self.assertEqual('noam', noam.get('id'))
        self.assertEqual(
            self.portal.absolute_url() + '/@users/noam',
            noam.get('@id')
        )
        self.assertEqual('noam.chomsky@example.com', noam.get('email'))
        self.assertEqual('Noam Avram Chomsky', noam.get('fullname'))
        self.assertEqual('web.mit.edu/chomsky', noam.get('home_page'))  # noqa
        self.assertEqual('Professor of Linguistics', noam.get('description'))  # noqa
        self.assertEqual('Cambridge, MA', noam.get('location'))

    def test_add_user(self):
        response = self.api_session.post(
            '/@users',
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "password": "peopleshistory"
            },
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        howard = api.user.get(userid='howard')
        self.assertEqual(
            "howard.zinn@example.com", howard.getProperty('email')
        )

    def test_add_user_username_is_required(self):
        response = self.api_session.post(
            '/@users',
            json={
                "password": "noamchomsky"
            },
        )
        transaction.commit()

        self.assertEqual(400, response.status_code)
        self.assertTrue('"Property \'username\' is required' in response.text)

    def test_add_user_password_is_required(self):
        response = self.api_session.post(
            '/@users',
            json={
                "username": "noamchomsky"
            },
        )
        transaction.commit()

        self.assertEqual(400, response.status_code)
        self.assertTrue('"Property \'password\' is required' in response.text)

    def test_add_user_email_is_required_if_email_login_is_enabled(self):
        # enable use_email_as_login
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.use_email_as_login = True
        transaction.commit()
        response = self.api_session.post(
            '/@users',
            json={
                "username": "noam",
                "password": "secret"
            },
        )

        self.assertEqual(400, response.status_code)
        self.assertTrue('"Property \'email\' is required' in response.text)

    def test_add_user_email_with_email_login_enabled(self):
        # enable use_email_as_login
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.use_email_as_login = True
        transaction.commit()
        response = self.api_session.post(
            '/@users',
            json={
                "email": "howard.zinn@example.com",
                "password": "secret"
            },
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        self.assertTrue(api.user.get(userid='howard.zinn@example.com'))

    def test_add_user_with_email_login_enabled(self):
        # enable use_email_as_login
        security_settings = getAdapter(self.portal, ISecuritySchema)
        security_settings.use_email_as_login = True
        transaction.commit()
        response = self.api_session.post(
            '/@users',
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "password": "secret"
            },
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        user = api.user.get(userid='howard.zinn@example.com')
        self.assertTrue(user)
        self.assertEqual('howard.zinn@example.com', user.getUserName())
        self.assertEqual('howard.zinn@example.com', user.getProperty('email'))

    def test_get_user(self):
        response = self.api_session.get('/@users/noam')

        self.assertEqual(response.status_code, 200)
        self.assertEqual('noam', response.json().get('id'))
        self.assertEqual(
            self.portal.absolute_url() + '/@users/noam',
            response.json().get('@id')
        )
        self.assertEqual(
            'noam.chomsky@example.com',
            response.json().get('email')
        )
        self.assertEqual('Noam Avram Chomsky', response.json().get('fullname'))
        self.assertEqual('web.mit.edu/chomsky', response.json().get('home_page'))  # noqa
        self.assertEqual('Professor of Linguistics', response.json().get('description'))  # noqa
        self.assertEqual('Cambridge, MA', response.json().get('location'))

    def test_get_search_user_with_filter(self):
        response = self.api_session.post(
            '/@users',
            json={
                "username": "howard",
                "email": "howard.zinn@example.com",
                "password": "peopleshistory"
            },
        )
        transaction.commit()
        response = self.api_session.get('/@users', params={'query': 'noa'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual('noam', response.json()[0].get('id'))
        self.assertEqual(
            self.portal.absolute_url() + '/@users/noam',
            response.json()[0].get('@id')
        )
        self.assertEqual(
            'noam.chomsky@example.com',
            response.json()[0].get('email')
        )
        self.assertEqual('Noam Avram Chomsky', response.json()[0].get('fullname'))  # noqa

        response = self.api_session.get('/@users', params={'query': 'howa'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual('howard', response.json()[0].get('id'))

    def test_get_non_existing_user(self):
        response = self.api_session.get('/@users/non-existing-user')

        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        payload = {
            'fullname': 'Noam A. Chomsky',
            'username': 'avram',
            'email': 'avram.chomsky@example.com'
        }
        response = self.api_session.patch('/@users/noam', json=payload)
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        noam = api.user.get(userid='noam')
        self.assertEqual('noam', noam.getUserId())  # user id never changes
        self.assertEqual('avram', noam.getUserName())
        self.assertEqual('Noam A. Chomsky', noam.getProperty('fullname'))
        self.assertEqual(
            'avram.chomsky@example.com',
            noam.getProperty('email')
        )

    def test_update_user_password(self):
        old_password_hashes = dict(
            self.portal.acl_users.source_users._user_passwords
        )
        payload = {'password': 'secret'}
        self.api_session.patch('/@users/noam', json=payload)
        transaction.commit()

        new_password_hashes = dict(
            self.portal.acl_users.source_users._user_passwords
        )
        self.assertNotEqual(
            old_password_hashes['noam'], new_password_hashes['noam']
        )

    def test_delete_user(self):
        response = self.api_session.delete('/@users/noam')
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(None, api.user.get(userid='noam'))

    def test_delete_non_existing_user(self):
        response = self.api_session.delete('/@users/non-existing-user')
        transaction.commit()

        self.assertEqual(response.status_code, 404)
