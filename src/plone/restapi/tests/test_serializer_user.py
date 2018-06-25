# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.component import getMultiAdapter

import unittest


class TestSerializeUserToJsonAdapter(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
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
        api.group.create(groupname='philosophers')
        api.group.add_user(groupname='philosophers', user=self.user)

    def serialize(self, user, **kwargs):
        serializer = getMultiAdapter((user, self.request),
                                     ISerializeToJson)
        return serializer(**kwargs)

    def test_serialize_returns_id(self):
        user = self.serialize(self.user)
        self.assertTrue(user)
        self.assertEqual('noam', user.get('id'))
        self.assertEqual('noam.chomsky@example.com', user.get('email'))
        self.assertEqual('Noam Avram Chomsky', user.get('fullname'))
        self.assertEqual('web.mit.edu/chomsky', user.get('home_page'))  # noqa
        self.assertEqual('Professor of Linguistics', user.get('description'))  # noqa
        self.assertEqual('Cambridge, MA', user.get('location'))

    def test_serialize_roles(self):
        user = self.serialize(self.user)
        self.assertIn('roles', user)
        self.assertNotIn('Authenticated', user['roles'])
        self.assertNotIn('Anonymous', user['roles'])

    def test_serialize_groups(self):
        user = self.serialize(self.user)
        self.assertNotIn('groups', user)

        user = self.serialize(self.user, include_groups=True)
        self.assertIn('groups', user)
        self.assertNotIn('AuthenticatedUsers', user['groups'])
        self.assertEqual(user['groups'][0]['id'], 'philosophers')
