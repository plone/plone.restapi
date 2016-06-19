# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

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
        self.assertTrue('admin' in user_ids)
        self.assertTrue('test_user_1_' in user_ids)
        self.assertTrue('noam' in user_ids)
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
                "email": "howard.zinn@bu.edu",
                "password": "peopleshistory"
            },
        )
        transaction.commit()

        self.assertEqual(201, response.status_code)
        howard = api.user.get(userid='howard')
        self.assertEqual("howard.zinn@bu.edu", howard.getProperty('email'))

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

    def test_update_user(self):
        payload = {'email': 'avram.chomsky@mit.edu'}
        response = self.api_session.patch('/@users/noam', json=payload)
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        noam = api.user.get(userid='noam')
        self.assertEqual('avram.chomsky@mit.edu', noam.getProperty('email'))

    def test_delete_user(self):
        response = self.api_session.delete('/@users/noam')
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(None, api.user.get(userid='noam'))
