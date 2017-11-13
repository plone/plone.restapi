# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.component import getMultiAdapter


import json
import unittest


class TestSiteSerializer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def serialize(self):
        serializer = getMultiAdapter((self.portal, self.request),
                                     ISerializeToJson)
        return serializer()

    def test_serializer_returns_json_serializeable_object(self):
        obj = self.serialize()
        self.assertTrue(isinstance(json.dumps(obj), str),
                        'Not JSON serializable')

    def test_serializer_includes_title(self):
        obj = self.serialize()
        self.assertIn(u'title', obj)
        self.assertEqual(u'Plone site', obj[u'title'])

    def test_get_is_folderish(self):
        obj = self.serialize()
        self.assertIn('is_folderish', obj)
        self.assertEquals(True, obj['is_folderish'])
