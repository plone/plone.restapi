from plone.dexterity.interfaces import IDexterityFTI
from plone.restapi.indexers import SearchableText_blocks
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from uuid import uuid4
from zope.component import queryUtility

import unittest


DRAFTJS_BLOCK = {
    "@type": "text",
    "text": {
        "blocks": [
            {
                "data": {},
                "depth": 0,
                "entityRanges": [],
                "inlineStyleRanges": [],
                "key": "behki",
                "text": "Plone is a powerful content management system",
                "type": "unstyled",
            }
        ],
        "entityMap": {},
    },
}

SLATE_BLOCK = {
    "@type": "slate",
    "plaintext": "Follow Plone Conference",
    "value": [{"children": [{"text": "Follow Plone Conference"}]}],
}


TABLE_BLOCK = {
    "@type": "table",
    "table": {
        "rows": [
            {
                "key": "a",
                "cells": [
                    {
                        "type": "data",
                        "key": "b",
                        "value": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "fgm98",
                                    "text": "My header",
                                    "type": "header-two",
                                },
                            ],
                            "entityMap": {},
                        },
                    },
                ],
            },
            {
                "key": "c",
                "cells": [
                    {
                        "type": "data",
                        "key": "d",
                        "value": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "mmm99",
                                    "text": "My data",
                                    "type": "text",
                                },
                            ],
                            "entityMap": {},
                        },
                    },
                ],
            },
        ]
    },
}


class TestSearchableTextIndexer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("volto.blocks")
        fti.behaviors = tuple(behavior_list)
        self.portal.invokeFactory(
            "Document",
            id="doc1",
            title="Title is here",
            description="Description is there",
            blocks={},
            blocks_layout={"items": []},
        )
        self.document = self.portal["doc1"]

    @staticmethod
    def _extract_searchable_text(obj):
        indexer = SearchableText_blocks(obj)
        return indexer()

    @staticmethod
    def _add_blocks(obj, raw_blocks):
        blocks = {str(uuid4()): block for block in raw_blocks}
        layout = list(blocks.keys())
        obj.blocks = blocks
        obj.blocks_layout["items"] = layout

    def test_indexer_no_blocks(self):
        result = self._extract_searchable_text(self.document)
        self.assertIn("Title is here", result)
        self.assertIn("Description is there", result)

    def test_indexer_block_has_searchableText(self):
        document = self.document
        self._add_blocks(
            document,
            [{"@type": "new-block", "attribute": "bar", "searchableText": "Foo Bar"}],
        )
        result = self._extract_searchable_text(document)
        self.assertIn("Title is here Description is there", result)
        self.assertIn("Foo Bar", result)

    def test_indexer_multiple_blocks(self):
        document = self.document
        self._add_blocks(
            document,
            [
                {"@type": "a-block", "key": "value", "searchableText": "Plone is a"},
                {"@type": "a-block", "attribute": "bar", "searchableText": "CMS"},
            ],
        )
        result = self._extract_searchable_text(document)
        self.assertIn("Plone is a CMS ", result)

    def test_indexer_block_slate_bbb(self):
        document = self.document
        self._add_blocks(
            document,
            [
                SLATE_BLOCK,
            ],
        )
        result = self._extract_searchable_text(document)
        self.assertIn("Title is here Description is there", result)
        self.assertIn("Follow Plone Conference", result)

    def test_indexer_block_text(self):
        document = self.document
        self._add_blocks(
            document,
            [
                DRAFTJS_BLOCK,
            ],
        )
        result = self._extract_searchable_text(document)
        self.assertIn("Title is here Description is there", result)
        self.assertIn("Plone is a powerful content management system", result)

    def test_indexer_block_table(self):
        document = self.document
        self._add_blocks(
            document,
            [
                TABLE_BLOCK,
            ],
        )
        result = self._extract_searchable_text(document)
        self.assertIn("Title is here Description is there", result)
        self.assertIn("My data", result)

    def test_indexer_block_with_subblocks(self):
        document = self.document
        block = {
            "@type": "complex-block",
            "blocks": {
                "ad625c27-670a-412e-821d-57870b6e82f1": SLATE_BLOCK,
                "80c5d58d-4baf-4adc-8ef4-36810df5628d": DRAFTJS_BLOCK,
                "4061b21d-c971-4ccc-a719-d8b24214fd8b": {
                    "@type": "old-complex-block",
                    "data": {
                        "blocks": {
                            "116feae0-7aa3-40f4-a776-fc893d78b353": TABLE_BLOCK,
                        }
                    },
                },
            },
        }
        self._add_blocks(
            document,
            [
                block,
            ],
        )
        result = self._extract_searchable_text(document)
        # From Slate sub block
        self.assertIn("Follow Plone Conference", result)
        # From DraftJS
        self.assertIn("Plone is a powerful content management system", result)
        # From Table block
        self.assertIn("My data", result)
