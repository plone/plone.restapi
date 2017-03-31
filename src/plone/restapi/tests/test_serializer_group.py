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
        self.gtool = api.portal.get_tool('portal_groups')
        properties = {
            'title': 'Plone Team',
            'description': 'We are Plone',
            'email': 'ploneteam@plone.org',
        }
        self.gtool.addGroup(
            'ploneteam', (), (),
            properties=properties,
            title=properties['title'],
            description=properties['description'])
        self.group = self.gtool.getGroupById('ploneteam')

    def serialize(self, user):
        serializer = getMultiAdapter((user, self.request),
                                     ISerializeToJson)
        return serializer()

    def test_serialize_returns_id(self):
        group = self.serialize(self.group)
        self.assertTrue(group)
        self.assertEqual('ploneteam', group.get('id'))
        self.assertEqual('ploneteam@plone.org', group.get('email'))
        self.assertEqual('Plone Team', group.get('title'))
        self.assertEqual('We are Plone', group.get('description'))
