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


class TestGroupsEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.gtool = api.portal.get_tool('portal_groups')
        properties = {
            'title': 'Plone Team',
            'description': 'We are Plone',
            'email': 'ploneteam@plone.org',
        }
        self.gtool.addGroup('ploneteam', (), (),
                            properties=properties,
                            title=properties['title'],
                            description=properties['description'])
        transaction.commit()

    def test_list_groups(self):
        response = self.api_session.get('/@groups')

        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.json()))
        user_ids = [group['id'] for group in response.json()]
        self.assertIn('Administrators', user_ids)
        self.assertIn('Reviewers', user_ids)
        self.assertIn('AuthenticatedUsers', user_ids)
        self.assertIn('ploneteam', user_ids)
        ptgroup = [x for x in response.json()
                   if x.get('groupname') == 'ploneteam'][0]
        self.assertEqual('ploneteam', ptgroup.get('id'))
        self.assertEqual(
            self.portal.absolute_url() + '/@groups/ploneteam',
            ptgroup.get('@id')
        )
        self.assertEqual('ploneteam@plone.org', ptgroup.get('email'))
        self.assertEqual('Plone Team', ptgroup.get('title'))
        self.assertEqual('We are Plone', ptgroup.get('description'))

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

    def test_get_group(self):
        response = self.api_session.get('/@groups/ploneteam')

        self.assertEqual(response.status_code, 200)
        self.assertEqual('ploneteam', response.json().get('id'))
        self.assertEqual(
            self.portal.absolute_url() + '/@groups/ploneteam',
            response.json().get('@id')
        )
        self.assertEqual(
            'ploneteam@plone.org',
            response.json().get('email')
        )
        self.assertEqual('ploneteam@plone.org', response.json().get('email'))
        self.assertEqual('Plone Team', response.json().get('title'))
        self.assertEqual('We are Plone', response.json().get('description'))

    def test_get_search_group_with_filter(self):
        response = self.api_session.get('/@groups', params={'query': 'plo'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual('ploneteam', response.json()[0].get('id'))
        self.assertEqual(
            self.portal.absolute_url() + '/@groups/ploneteam',
            response.json()[0].get('@id')
        )
        self.assertEqual(
            'ploneteam@plone.org',
            response.json()[0].get('email')
        )

        response = self.api_session.get('/@groups', params={'query': 'Auth'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual('AuthenticatedUsers', response.json()[0].get('id'))

    def test_get_non_existing_group(self):
        response = self.api_session.get('/@groups/non-existing-group')

        self.assertEqual(response.status_code, 404)
