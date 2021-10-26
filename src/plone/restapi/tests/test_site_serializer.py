# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.component import getMultiAdapter

import json
import unittest


class TestSiteSerializer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.portal.invokeFactory(
            "Document",
            id=u"doc1",
        )

    def serialize(self):
        serializer = getMultiAdapter((self.portal, self.request), ISerializeToJson)
        return serializer()

    def test_serializer_returns_json_serializeable_object(self):
        obj = self.serialize()
        self.assertTrue(isinstance(json.dumps(obj), str), "Not JSON serializable")

    def test_serializer_includes_title(self):
        obj = self.serialize()
        self.assertIn(u"title", obj)
        self.assertEqual(u"Plone site", obj[u"title"])

    def test_get_is_folderish(self):
        obj = self.serialize()
        self.assertIn("is_folderish", obj)
        self.assertEqual(True, obj["is_folderish"])

    def test_resolveuids_get_serialized_in_serializer(self):
        blocks = {
            "0358abe2-b4f1-463d-a279-a63ea80daf19": {
                "@type": "foo",
                "url": "resolveuid/{}".format(self.portal.doc1.UID()),
            },
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
        }
        self.portal.blocks = json.dumps(blocks)
        obj = self.serialize()
        self.assertEqual(
            obj["blocks"]["0358abe2-b4f1-463d-a279-a63ea80daf19"]["url"],
            self.portal.doc1.absolute_url(),
        )
