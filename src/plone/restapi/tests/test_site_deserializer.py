from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.tests.mixin_ordering import OrderingMixin
from zope.component import getMultiAdapter

import json
import unittest


class TestDXContentDeserializer(unittest.TestCase, OrderingMixin):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        # ordering setup
        self.folder = self.portal

        for x in range(1, 10):
            self.folder.invokeFactory(
                "Document", id="doc" + str(x), title="Test doc " + str(x)
            )

    def deserialize(self, body="{}", validate_all=False, context=None):
        context = context or self.portal
        self.request["BODY"] = body
        deserializer = getMultiAdapter((context, self.request), IDeserializeFromJson)
        return deserializer(validate_all=validate_all)

    def test_set_layout(self):
        current_layout = self.portal.getLayout()
        self.assertNotEqual(current_layout, "my_new_layout")
        self.deserialize(body='{"layout": "my_new_layout"}')
        self.assertEqual("my_new_layout", self.portal.getLayout())


class TestSiteRootDeserializer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.portal.invokeFactory(
            "Document",
            id="doc1",
        )

    def deserialize(self, body="{}", validate_all=False, context=None):
        context = context or self.portal
        self.request["BODY"] = body
        deserializer = getMultiAdapter((context, self.request), IDeserializeFromJson)
        return deserializer(validate_all=validate_all)

    def test_opt_in_blocks_deserializer(self):
        blocks = {
            "0358abe2-b4f1-463d-a279-a63ea80daf19": {"@type": "description"},
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
        }
        blocks_layout = {
            "items": [
                "07c273fc-8bfc-4e7d-a327-d513e5a945bb",
                "0358abe2-b4f1-463d-a279-a63ea80daf19",
            ]
        }

        self.deserialize(
            body='{{"blocks": {}, "blocks_layout": {}}}'.format(
                json.dumps(blocks), json.dumps(blocks_layout)
            )
        )

        self.assertEqual(blocks, json.loads(self.portal.blocks))
        self.assertEqual(blocks_layout, json.loads(self.portal.blocks_layout))

    def test_resolveuids_blocks_deserializer(self):
        blocks = {
            "0358abe2-b4f1-463d-a279-a63ea80daf19": {
                "@type": "foo",
                "url": self.portal.doc1.absolute_url(),
            },
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
        }
        blocks_layout = {
            "items": [
                "07c273fc-8bfc-4e7d-a327-d513e5a945bb",
                "0358abe2-b4f1-463d-a279-a63ea80daf19",
            ]
        }

        self.deserialize(
            body='{{"blocks": {}, "blocks_layout": {}}}'.format(
                json.dumps(blocks), json.dumps(blocks_layout)
            )
        )

        values = json.loads(self.portal.blocks)
        self.assertEqual(
            values["0358abe2-b4f1-463d-a279-a63ea80daf19"]["url"],
            f"resolveuid/{self.portal.doc1.UID()}",
        )
