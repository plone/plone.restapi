"""
Test the deserializer for the portal root.
"""

from importlib import import_module
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.schema import SCHEMA_CACHE
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi import testing
from plone.restapi.tests.mixin_ordering import OrderingMixin
from zope.component import getMultiAdapter
from zope.component import queryUtility

import json
import unittest

HAS_PLONE_6 = getattr(
    import_module("Products.CMFPlone.factory"), "PLONE60MARKER", False
)


class TestDXContentDeserializer(testing.PloneRestAPITestCase, OrderingMixin):
    """
    Test the deserializer for local sites.
    """

    def setUp(self):
        """
        Set up a content type and instance to test against.
        """
        super().setUp()

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


class TestSiteRootDeserializer(testing.PloneRestAPITestCase):
    """
    Test the deserializer for the portal root.
    """

    def setUp(self):
        """
        Create a content instance to test against.
        """
        super().setUp()

        self.portal.invokeFactory(
            "Document",
            id="doc1",
        )

        # Enable volto.blocks if Plone Site is DX
        fti = queryUtility(IDexterityFTI, name="Plone Site")
        if fti is not None:
            behavior_list = [a for a in fti.behaviors]
            behavior_list.append("volto.blocks")
            fti.behaviors = tuple(behavior_list)
            # Invalidating the cache is required for the FTI to be applied
            # on the existing object
            SCHEMA_CACHE.invalidate("Plone Site")

    def deserialize(self, body="{}", validate_all=False, context=None):
        context = context or self.portal
        self.request["BODY"] = body
        deserializer = getMultiAdapter((context, self.request), IDeserializeFromJson)
        return deserializer(validate_all=validate_all)

    @unittest.skipIf(
        HAS_PLONE_6,
        "This test is only intended to run for Plone 5 and the blocks behavior site root hack enabled",
    )
    def test_opt_in_blocks_deserializer_plone5(self):
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

    @unittest.skipIf(
        HAS_PLONE_6,
        "This test is only intended to run for Plone 5 and the blocks behavior site root hack enabled",
    )
    def test_resolveuids_blocks_deserializer_plone5(self):
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

    @unittest.skipIf(
        not HAS_PLONE_6,
        "This test is only intended to run for Plone 6 and DX site root enabled",
    )
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

        self.assertEqual(blocks, self.portal.blocks)
        self.assertEqual(blocks_layout, self.portal.blocks_layout)

    @unittest.skipIf(
        not HAS_PLONE_6,
        "This test is only intended to run for Plone 6 and DX site root enabled",
    )
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

        values = self.portal.blocks
        self.assertEqual(
            values["0358abe2-b4f1-463d-a279-a63ea80daf19"]["url"],
            f"resolveuid/{self.portal.doc1.UID()}",
        )
