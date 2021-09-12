from plone.dexterity.interfaces import IDexterityFTI
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.component import queryUtility

import json
import unittest

try:
    from Products.CMFPlone.factory import PLONE60MARKER

    PLONE60MARKER  # pyflakes
except ImportError:
    PLONE_6 = False
else:
    PLONE_6 = True


class TestSiteSerializer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.portal.invokeFactory(
            "Document",
            id="doc1",
        )

        fti = queryUtility(IDexterityFTI, name="Plone Site")
        if fti is not None:
            behavior_list = [a for a in fti.behaviors]
            behavior_list.append("volto.blocks")
            fti.behaviors = tuple(behavior_list)

    def serialize(self):
        serializer = getMultiAdapter((self.portal, self.request), ISerializeToJson)
        return serializer()

    def test_serializer_returns_json_serializeable_object(self):
        obj = self.serialize()
        self.assertTrue(isinstance(json.dumps(obj), str), "Not JSON serializable")

    def test_serializer_includes_title(self):
        obj = self.serialize()
        self.assertIn("title", obj)
        self.assertEqual("Plone site", obj["title"])

    def test_get_is_folderish(self):
        obj = self.serialize()
        self.assertIn("is_folderish", obj)
        self.assertEqual(True, obj["is_folderish"])

    @unittest.skipIf(
        PLONE_6,
        "This test is only intended to run for Plone 5 and the blocks behavior site root hack enabled",
    )
    def test_resolveuids_get_serialized_in_serializer_plone5(self):
        blocks = {
            "0358abe2-b4f1-463d-a279-a63ea80daf19": {
                "@type": "foo",
                "url": f"resolveuid/{self.portal.doc1.UID()}",
            },
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
        }
        self.portal.blocks = json.dumps(blocks)
        obj = self.serialize()
        self.assertEqual(
            obj["blocks"]["0358abe2-b4f1-463d-a279-a63ea80daf19"]["url"],
            self.portal.doc1.absolute_url(),
        )

    @unittest.skipIf(
        not PLONE_6,
        "This test is only intended to run for Plone 6 and DX site root enabled",
    )
    def test_resolveuids_get_serialized_in_serializer(self):
        blocks = {
            "0358abe2-b4f1-463d-a279-a63ea80daf19": {
                "@type": "foo",
                "url": f"resolveuid/{self.portal.doc1.UID()}",
            },
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
        }
        self.portal.blocks = blocks
        obj = self.serialize()
        self.assertEqual(
            obj["blocks"]["0358abe2-b4f1-463d-a279-a63ea80daf19"]["url"],
            self.portal.doc1.absolute_url(),
        )
