from plone.dexterity.interfaces import IDexterityFTI
from plone.restapi.blocks import visit_blocks
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.component import queryUtility

import unittest

# (key, @type) pairs of Plate regions. Regions are found by ``@type``, not key.
# ``__somersault__`` is the deprecated legacy name.
PLATE_REGIONS = (
    ("main", "plate"),
    ("aboveContent", "plate"),
    ("__somersault__", "__somersault__"),
)


class TestBlocksVisitor(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("volto.blocks")
        fti.behaviors = tuple(behavior_list)

        self.doc = self.portal.invokeFactory("Document", id="doc1")

    def test_visit_blocks(self):
        visited = []
        blocks = {
            "123": {
                "@id": "block1",
                "blocks": {
                    "456": {
                        "@id": "block2",
                    }
                },
            }
        }
        for block in visit_blocks(self.doc, blocks):
            visited.append(block["@id"])
        # depth-first traversal
        self.assertEqual(visited, ["block2", "block1"])

    def test_visit_blocks_in_plate_value(self):
        for key, block_type in PLATE_REGIONS:
            with self.subTest(key=key, block_type=block_type):
                visited = []
                blocks = {
                    key: {
                        "@type": block_type,
                        "value": [
                            {
                                "type": "p",
                                "children": [{"@type": "image"}],
                            }
                        ],
                    }
                }
                for block in visit_blocks(self.doc, blocks):
                    visited.append(block["@type"])
                # depth-first traversal
                self.assertEqual(visited, ["image", block_type])
