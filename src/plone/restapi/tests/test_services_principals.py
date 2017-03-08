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


class TestPrincipalsEndpoint(unittest.TestCase):

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

        properties = {
            'email': 'noam.chomsky@example.com',
            'username': 'noamchomsky',
            'fullname': 'Noam Avram Chomsky',
            'home_page': 'web.mit.edu/chomsky',
            'description': 'Professor of Linguistics',
            'location': 'Cambridge, MA'
        }
        self.user = api.user.create(
            email='noam.chomsky@example.com',
            username='noam',
            properties=properties
        )

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

    def test_get_principals(self):
        response = self.api_session.get(
            '/@principals',
            params={
                "search": "noam"
            }
        )
        self.assertEqual(200, response.status_code)

        response = response.json()
        self.assertEqual(2, len(response))
        self.assertEquals(1, len(response['users']))
        self.assertEquals('noam', response['users'][0]['id'])

        response = self.api_session.get(
            '/@principals',
            params={
                "search": "plone"
            }
        )
        self.assertEqual(200, response.status_code)

        response = response.json()
        self.assertEqual(2, len(response))
        self.assertEquals(1, len(response['groups']))
        self.assertEquals('ploneteam', response['groups'][0]['id'])

    def test_get_principals_response_both(self):
        self.user = api.user.create(
            email='plone.user@example.com',
            username='plone.user'
        )
        transaction.commit()

        response = self.api_session.get(
            '/@principals',
            params={
                "search": "plone"
            }
        )
        self.assertEqual(200, response.status_code)

        response = response.json()
        self.assertEqual(2, len(response))
        self.assertEquals(1, len(response['users']))
        self.assertEquals(1, len(response['groups']))
        self.assertEquals('plone.user', response['users'][0]['id'])
        self.assertEquals('ploneteam', response['groups'][0]['id'])
