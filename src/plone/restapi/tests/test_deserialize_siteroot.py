# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.component import getMultiAdapter

import json
import unittest


class TestDXContentDeserializer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def deserialize(self, body='{}', validate_all=False, context=None):
        context = context or self.portal
        self.request['BODY'] = body
        deserializer = getMultiAdapter((context, self.request),
                                       IDeserializeFromJson)
        return deserializer(validate_all=validate_all)

    def test_opt_in_tiles_deserializer(self):
        tiles = {
            "0358abe2-b4f1-463d-a279-a63ea80daf19": {
                "@type": "description"
            },
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {
                "@type": "title"
            }
        }
        tiles_layout = {
            "items": [
                "07c273fc-8bfc-4e7d-a327-d513e5a945bb",
                "0358abe2-b4f1-463d-a279-a63ea80daf19"
            ]
        }

        self.deserialize(
            body='{{"tiles": {}, "tiles_layout": {}}}'.format(
                json.dumps(tiles), json.dumps(tiles_layout)))

        self.assertEqual(tiles, json.loads(self.portal.tiles))
        self.assertEqual(tiles_layout, json.loads(self.portal.tiles_layout))
