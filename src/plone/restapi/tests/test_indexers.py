from plone.dexterity.interfaces import IDexterityFTI
from plone.restapi.testing import PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
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

PLATE_BLOCK = {
    "@type": "__somersault__",
    "value": [
        {
            "blockWidth": "default",
            "children": [{"text": "Wiki Page"}],
            "id": "R7I1TseJfZ",
            "type": "title",
        },
        {
            "blockWidth": "default",
            "children": [
                {
                    "text": "Lorem ipsum dolor sit amet odio tortor in sollicitudin phasellus interdum justo. Arcu hendrerit pretium nisi praesent tempus netus non neque blandit vel. Augue molestie cras fames vestibulum convallis facilisi hac imperdiet fermentum. Blandit phasellus nullam auctor elit enim eu mollis aliquet adipiscing feugiat dui lacus luctus. Mauris hendrerit facilisis est nunc turpis pharetra eleifend duis porta platea nulla tortor aliquam est."
                }
            ],
            "id": "3Kp3XjHEfX",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [
                {
                    "text": "Quam luctus pulvinar urna egestas cras nisi eget sollicitudin aliquet sodales do. Iaculis lobortis viverra lacus sagittis mauris leo porttitor. Platea fames maecenas posuere sapien interdum a do. Senectus adipiscing senectus aliqua porta nec quam non tempor adipiscing. Suspendisse tristique gravida congue molestie mollis bibendum est ac proin lacinia. elephant "
                }
            ],
            "id": "HURTN0Xplu",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Images\n"}],
            "id": "n7g-i7nUCD",
            "type": "h2",
        },
        {
            "align": "center",
            "blockWidth": "default",
            "children": [{"text": ""}],
            "credit": {},
            "description": "",
            "id": "JpNvN48GZB",
            "image_field": "image",
            "image_scales": {
                "image": [
                    {
                        "content-type": "image/jpeg",
                        "download": "@@images/image-2400-1bb0eacaa1f242697c99f16390acb188.jpeg",
                        "filename": "black-starry-night.jpg",
                        "height": 1708,
                        "scales": {
                            "2k": {
                                "download": "@@images/image-2000-3392a7d7f081a956cbcc692f8883d0c1.jpeg",
                                "height": 1423,
                                "width": 2000,
                            },
                            "great": {
                                "download": "@@images/image-1200-909481f59700410df495646a052dc3b1.jpeg",
                                "height": 854,
                                "width": 1200,
                            },
                            "huge": {
                                "download": "@@images/image-1600-a6e6167b39388fef4b526133c1870e40.jpeg",
                                "height": 1138,
                                "width": 1600,
                            },
                            "icon": {
                                "download": "@@images/image-32-9a669847a569c3298c7721e3ff2f4304.jpeg",
                                "height": 22,
                                "width": 32,
                            },
                            "large": {
                                "download": "@@images/image-800-a4acb10ae66ba59e8def9bf3b71dd736.jpeg",
                                "height": 569,
                                "width": 800,
                            },
                            "larger": {
                                "download": "@@images/image-1000-dc0e9da8b33ea5733e9754478d1d36b8.jpeg",
                                "height": 711,
                                "width": 1000,
                            },
                            "mini": {
                                "download": "@@images/image-200-b3778482f1b185e664f87c62ebaf91b3.jpeg",
                                "height": 142,
                                "width": 200,
                            },
                            "preview": {
                                "download": "@@images/image-400-e472369a7fe4b7d61a838614af838406.jpeg",
                                "height": 284,
                                "width": 400,
                            },
                            "teaser": {
                                "download": "@@images/image-600-5ad744a40f6615296c5f7f4bf631e3ac.jpeg",
                                "height": 427,
                                "width": 600,
                            },
                            "thumb": {
                                "download": "@@images/image-128-e22984039f956f8151d0ba444712ccbb.jpeg",
                                "height": 91,
                                "width": 128,
                            },
                            "tile": {
                                "download": "@@images/image-64-7e932c9d8adfe0b8e0ad6386e264a3b9.jpeg",
                                "height": 45,
                                "width": 64,
                            },
                        },
                        "size": 693013,
                        "width": 2400,
                    }
                ]
            },
            "size": "l",
            "styles": {
                "blockWidth:noprefix": {
                    "--block-width": "var(--default-container-width)"
                }
            },
            "theme": "default",
            "title": "black-starry-night.jpg",
            "type": "img",
            "url": "http://localhost:3000/wiki-page/black-starry-night.jpg",
        },
        {
            "align": "left",
            "blockWidth": "default",
            "children": [{"text": ""}],
            "credit": {},
            "description": "",
            "id": "pwOJYQ3VHm",
            "image_field": "image",
            "image_scales": {
                "image": [
                    {
                        "content-type": "image/png",
                        "download": "@@images/image-2000-f7c0b45d8fb7dacb43f858ce3b043033.png",
                        "filename": "plone-foundation.png",
                        "height": 439,
                        "scales": {
                            "2k": {
                                "download": "@@images/image-2000-b97cc79475c3e4b78159844401ffd5b5.png",
                                "height": 439,
                                "width": 2000,
                            },
                            "great": {
                                "download": "@@images/image-1200-c79cfd78438c0219dfb6fa238bd07059.png",
                                "height": 263,
                                "width": 1200,
                            },
                            "huge": {
                                "download": "@@images/image-1600-e7049d9b2a69a2c78214ae7fb23fd247.png",
                                "height": 351,
                                "width": 1600,
                            },
                            "icon": {
                                "download": "@@images/image-32-eba9ceff013fd045141a03085961208e.png",
                                "height": 7,
                                "width": 32,
                            },
                            "large": {
                                "download": "@@images/image-800-2baf515d696515d24f157edff7d5500c.png",
                                "height": 175,
                                "width": 800,
                            },
                            "larger": {
                                "download": "@@images/image-1000-3aad43738f471d3dacadec2762146c3c.png",
                                "height": 219,
                                "width": 1000,
                            },
                            "mini": {
                                "download": "@@images/image-200-a79dc1f6b295196fc4808aafaf3c1083.png",
                                "height": 43,
                                "width": 200,
                            },
                            "preview": {
                                "download": "@@images/image-400-2d6d8ed83e23d421cb7c2a8d80ead210.png",
                                "height": 87,
                                "width": 400,
                            },
                            "teaser": {
                                "download": "@@images/image-600-8225a92e34c5d64b17522b688e62270b.png",
                                "height": 131,
                                "width": 600,
                            },
                            "thumb": {
                                "download": "@@images/image-128-2192266ed097c2df06bacaf703dfd273.png",
                                "height": 28,
                                "width": 128,
                            },
                            "tile": {
                                "download": "@@images/image-64-0b0ad172a2c3a90afb779f7902dea6fc.png",
                                "height": 14,
                                "width": 64,
                            },
                        },
                        "size": 50737,
                        "width": 2000,
                    }
                ]
            },
            "size": "s",
            "styles": {
                "blockWidth:noprefix": {
                    "--block-width": "var(--narrow-container-width)"
                },
                "size:noprefix": "small",
            },
            "theme": "grey",
            "title": "Plone Foundation Logo",
            "type": "img",
            "url": "http://localhost:3000/images/plone-foundation.png",
        },
        {
            "blockWidth": "default",
            "children": [
                {"bold": True, "text": "Lorem ipsum"},
                {"text": " dolor sit amet odio "},
                {"italic": True, "text": "tortor"},
                {
                    "text": " in sollicitudin phasellus interdum justo. Arcu hendrerit pretium nisi praesent tempus netus non neque blandit vel. Augue molestie cras fames vestibulum convallis facilisi hac imperdiet fermentum. Blandit phasellus nullam auctor elit enim eu mollis aliquet adipiscing feugiat dui lacus luctus. "
                },
                {"code": True, "text": "Mauris hendrerit"},
                {
                    "text": " facilisis est nunc turpis pharetra eleifend duis porta platea nulla tortor aliquam est."
                },
            ],
            "id": "sZrMoBoRjY",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [
                {
                    "text": "Quam luctus pulvinar urna egestas cras nisi eget sollicitudin aliquet sodales do. Iaculis lobortis viverra lacus sagittis mauris leo porttitor. Platea fames maecenas posuere sapien interdum a do. Senectus adipiscing senectus aliqua porta nec quam non tempor adipiscing. "
                },
                {"code": True, "text": "Suspendisse"},
                {
                    "text": " tristique gravida congue molestie mollis bibendum est ac proin lacinia."
                },
            ],
            "id": "i7lDvzFKId",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Heading 3"}],
            "id": "6k6g1tdhjy",
            "type": "h3",
        },
        {
            "blockWidth": "default",
            "children": [
                {
                    "text": "Lorem ipsum dolor sit amet odio tortor in sollicitudin phasellus interdum justo. Arcu hendrerit pretium nisi praesent tempus netus non neque blandit vel. Augue molestie cras fames vestibulum convallis facilisi hac imperdiet fermentum. Blandit phasellus nullam auctor elit enim eu mollis aliquet adipiscing feugiat dui lacus luctus. Mauris hendrerit facilisis est nunc turpis pharetra eleifend duis porta platea nulla tortor aliquam est."
                }
            ],
            "id": "d6i1e5x12C",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Heading 4"}],
            "id": "KCAHgIpuiP",
            "type": "h4",
        },
        {
            "blockWidth": "default",
            "children": [
                {
                    "text": "Lorem ipsum dolor sit amet odio tortor in sollicitudin phasellus interdum justo. Arcu hendrerit pretium nisi praesent tempus netus non neque blandit vel. Augue molestie cras fames vestibulum convallis facilisi hac imperdiet fermentum. Blandit phasellus nullam auctor elit enim eu mollis aliquet adipiscing feugiat dui lacus luctus. Mauris hendrerit facilisis est nunc turpis pharetra eleifend duis porta platea nulla tortor aliquam est."
                }
            ],
            "id": "M9-U-xW9SN",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Links"}],
            "id": "jwdR0vaYZU",
            "type": "h2",
        },
        {
            "blockWidth": "default",
            "children": [
                {"text": ""},
                {
                    "blockWidth": "default",
                    "children": [{"text": "This is a link"}],
                    "id": "LR0yRMwNPU",
                    "type": "a",
                    "url": "http://localhost:3000/images",
                },
                {"text": ""},
            ],
            "id": "IR4xX0-rK0",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Bulleted Lists"}],
            "id": "_cqbTfwYnN",
            "type": "h2",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "item 1"}],
            "id": "K6amx9O4Qe",
            "indent": 1,
            "listStyleType": "disc",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "item 2"}],
            "id": "Rdun1rD9a8",
            "indent": 1,
            "listStart": 2,
            "listStyleType": "disc",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "item nested 1"}],
            "id": "52XplNhNHY",
            "indent": 2,
            "listStyleType": "disc",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Numbered lists"}],
            "id": "GkZBwjoSC2",
            "type": "h2",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "item 1"}],
            "id": "N0QvWn_wh4",
            "indent": 1,
            "listRestartPolite": 1,
            "listStyleType": "decimal",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "item 2"}],
            "id": "aqQGyzW-79",
            "indent": 1,
            "listStart": 2,
            "listStyleType": "decimal",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "item nested 1"}],
            "id": "moU8i2MrAo",
            "indent": 2,
            "listStyleType": "decimal",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "ToDo list"}],
            "id": "wZk0XsUILT",
            "type": "h2",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "ToDo list item 1"}],
            "id": "Z3bev6Y3x-",
            "indent": 1,
            "listStyleType": "todo",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "checked": True,
            "children": [{"text": "ToDo list item 2"}],
            "id": "r8HwnJkANA",
            "indent": 1,
            "listStart": 2,
            "listStyleType": "todo",
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Toggle items (collapsibles)"}],
            "id": "MsbUIn1l-e",
            "type": "h2",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "This is a toggle item"}],
            "id": "ZtFH1V5VbH",
            "type": "toggle",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "With collapsible text inside"}],
            "id": "zBMhIVCfyG",
            "indent": 1,
            "type": "p",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Code"}],
            "id": "LID0KLs_8q",
            "type": "h2",
        },
        {
            "blockWidth": "default",
            "children": [
                {
                    "blockWidth": "default",
                    "children": [{"text": "from plone import api"}],
                    "id": "4x8ZCzV4_C",
                    "type": "code_line",
                },
                {
                    "blockWidth": "default",
                    "children": [{"text": ""}],
                    "id": "zpN-hqZwsi",
                    "type": "code_line",
                },
                {
                    "blockWidth": "default",
                    "children": [
                        {"text": 'brains = api.content.find(portal_type="WikiPage")'}
                    ],
                    "id": "iKrnnE152j",
                    "type": "code_line",
                },
                {
                    "blockWidth": "default",
                    "children": [{"text": "for brain in brains:"}],
                    "id": "msc_Df5asY",
                    "type": "code_line",
                },
                {
                    "blockWidth": "default",
                    "children": [{"text": "    print(brain.Title)"}],
                    "id": "8_U5v15Wv_",
                    "type": "code_line",
                },
                {
                    "blockWidth": "default",
                    "children": [{"text": " "}],
                    "id": "oEGjq9wRfX",
                    "type": "code_line",
                },
            ],
            "id": "1HtHs7cBq8",
            "lang": "python",
            "type": "code_block",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Tables"}],
            "id": "-SiubNCFsU",
            "type": "h2",
        },
        {
            "blockWidth": "default",
            "children": [
                {
                    "blockWidth": "default",
                    "children": [
                        {
                            "blockWidth": "default",
                            "children": [
                                {
                                    "blockWidth": "default",
                                    "children": [{"text": "Header 1"}],
                                    "id": "XPZB9k7A_O",
                                    "type": "p",
                                }
                            ],
                            "id": "34zB7tsQuA",
                            "type": "td",
                        },
                        {
                            "blockWidth": "default",
                            "children": [
                                {
                                    "blockWidth": "default",
                                    "children": [{"text": "Header 2"}],
                                    "id": "sUuGGPqaCe",
                                    "type": "p",
                                }
                            ],
                            "id": "S1z5N7hRtV",
                            "type": "td",
                        },
                        {
                            "blockWidth": "default",
                            "children": [
                                {
                                    "blockWidth": "default",
                                    "children": [{"text": "different widths"}],
                                    "id": "CT-5hB1BeT",
                                    "type": "p",
                                }
                            ],
                            "colSpan": 1,
                            "id": "rqwSe1ZNIi",
                            "rowSpan": 1,
                            "type": "td",
                        },
                        {
                            "blockWidth": "default",
                            "borders": {"right": {"size": 0}, "top": {"size": 0}},
                            "children": [
                                {
                                    "blockWidth": "default",
                                    "children": [{"text": "and borders"}],
                                    "id": "YLR0BX6IWm",
                                    "type": "p",
                                }
                            ],
                            "colSpan": 1,
                            "id": "BNF3uHQp7_",
                            "rowSpan": 1,
                            "type": "td",
                        },
                    ],
                    "id": "NWEyO-n86Q",
                    "type": "tr",
                },
                {
                    "blockWidth": "default",
                    "children": [
                        {
                            "blockWidth": "default",
                            "children": [
                                {
                                    "blockWidth": "default",
                                    "children": [{"text": "Merged cells"}],
                                    "id": "Xk7ZIMyGld",
                                    "type": "p",
                                }
                            ],
                            "colSpan": 2,
                            "id": "7b0R3wmddK",
                            "rowSpan": 1,
                            "type": "td",
                        },
                        {
                            "blockWidth": "default",
                            "children": [
                                {
                                    "blockWidth": "default",
                                    "children": [{"text": ""}],
                                    "id": "iDfGbSKjTQ",
                                    "type": "p",
                                }
                            ],
                            "colSpan": 1,
                            "id": "kTT7k0XoPZ",
                            "rowSpan": 1,
                            "type": "td",
                        },
                        {
                            "background": "#4B85E8",
                            "blockWidth": "default",
                            "children": [
                                {
                                    "blockWidth": "default",
                                    "children": [{"text": "and backgrounds"}],
                                    "id": "XxSuKW1hZ3",
                                    "type": "p",
                                }
                            ],
                            "colSpan": 1,
                            "id": "t612mnrE7y",
                            "rowSpan": 1,
                            "type": "td",
                        },
                    ],
                    "id": "Uj6_EOM1Wp",
                    "type": "tr",
                },
            ],
            "colSizes": [0, 0, 470, 0],
            "id": "2Yz2b5CMm0",
            "type": "table",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Blockquote"}],
            "id": "ABs91fnktj",
            "type": "h2",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "This is a blockquote"}],
            "id": "vjfZbY4TJi",
            "type": "blockquote",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Callouts"}],
            "id": "1z77VtReID",
            "type": "h2",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "This is a callout"}],
            "icon": "\ud83d\udca1",
            "id": "AbGgC_GM2l",
            "type": "callout",
        },
        {
            "blockWidth": "default",
            "children": [{"text": "Table of contents"}],
            "id": "Ixkw1BK8mD",
            "type": "h2",
        },
        {
            "blockWidth": "default",
            "children": [{"text": ""}],
            "id": "8mxTgibI62",
            "type": "toc",
        },
        {
            "blockWidth": "default",
            "children": [{"text": ""}],
            "id": "1WXuAaHdQ3",
            "type": "p",
        },
    ],
}


class TestSearchableTextIndexer(unittest.TestCase):

    layer = PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.catalog = getToolByName(self.portal, "portal_catalog")
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

    def _extract_searchable_text(self, obj):
        query = {"path": {"query": "/".join(obj.getPhysicalPath()), "depth": 0}}
        brains = self.catalog(query)
        brain = brains[0]
        data = self.catalog.getIndexDataForRID(brain.getRID())
        return " ".join(data["SearchableText"])

    @staticmethod
    def _add_blocks(obj, raw_blocks):
        blocks = {str(uuid4()): block for block in raw_blocks}
        layout = list(blocks.keys())
        obj.blocks = blocks
        obj.blocks_layout["items"] = layout
        obj.reindexObject()

    def test_indexer_no_blocks(self):
        result = self._extract_searchable_text(self.document)
        self.assertIn("title is here", result)
        self.assertIn("description is there", result)

    def test_indexer_block_has_searchableText(self):
        document = self.document
        self._add_blocks(
            document,
            [{"@type": "new-block", "attribute": "bar", "searchableText": "Foo Bar"}],
        )
        result = self._extract_searchable_text(document)
        self.assertIn("title is here description is there", result)
        self.assertIn("foo bar", result)

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
        self.assertIn("plone is a cms", result)

    def test_indexer_block_slate_bbb(self):
        document = self.document
        self._add_blocks(
            document,
            [
                SLATE_BLOCK,
            ],
        )
        result = self._extract_searchable_text(document)
        self.assertIn("title is here description is there", result)
        self.assertIn("follow plone conference", result)

    def test_indexer_block_text(self):
        document = self.document
        self._add_blocks(
            document,
            [
                DRAFTJS_BLOCK,
            ],
        )
        result = self._extract_searchable_text(document)
        self.assertIn("title is here description is there", result)
        self.assertIn("plone is a powerful content management system", result)

    def test_indexer_block_table(self):
        document = self.document
        self._add_blocks(
            document,
            [
                TABLE_BLOCK,
            ],
        )
        result = self._extract_searchable_text(document)
        self.assertIn("title is here description is there", result)
        self.assertIn("my data", result)

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
        self.assertIn("follow plone conference", result)
        # From DraftJS
        self.assertIn("plone is a powerful content management system", result)
        # From Table block
        self.assertIn("my data", result)

    def test_indexer_block_plate(self):
        document = self.document
        document.blocks = {
            "__somersault__": PLATE_BLOCK,
        }
        document.reindexObject()
        result = self._extract_searchable_text(document)
        self.assertIn(
            "wiki page lorem ipsum dolor sit amet odio tortor in sollicitudin phasellus interdum justo arcu hendrerit pretium nisi praesent tempus netus non neque blandit vel augue molestie cras fames vestibulum convallis facilisi hac imperdiet fermentum blandit phasellus nullam auctor elit enim eu mollis aliquet adipiscing feugiat dui lacus luctus mauris hendrerit facilisis est nunc turpis pharetra eleifend duis porta platea nulla tortor aliquam est quam luctus pulvinar urna egestas cras nisi eget sollicitudin aliquet sodales do iaculis lobortis viverra lacus sagittis mauris leo porttitor platea fames maecenas posuere sapien interdum a do senectus adipiscing senectus aliqua porta nec quam non tempor adipiscing suspendisse tristique gravida congue molestie mollis bibendum est ac proin lacinia elephant images lorem ipsum dolor sit amet odio tortor in sollicitudin phasellus interdum justo arcu hendrerit pretium nisi praesent tempus netus non neque blandit vel augue molestie cras fames vestibulum convallis facilisi hac imperdiet fermentum blandit phasellus nullam auctor elit enim eu mollis aliquet adipiscing feugiat dui lacus luctus mauris hendrerit facilisis est nunc turpis pharetra eleifend duis porta platea nulla tortor aliquam est quam luctus pulvinar urna egestas cras nisi eget sollicitudin aliquet sodales do iaculis lobortis viverra lacus sagittis mauris leo porttitor platea fames maecenas posuere sapien interdum a do senectus adipiscing senectus aliqua porta nec quam non tempor adipiscing suspendisse tristique gravida congue molestie mollis bibendum est ac proin lacinia heading 3 lorem ipsum dolor sit amet odio tortor in sollicitudin phasellus interdum justo arcu hendrerit pretium nisi praesent tempus netus non neque blandit vel augue molestie cras fames vestibulum convallis facilisi hac imperdiet fermentum blandit phasellus nullam auctor elit enim eu mollis aliquet adipiscing feugiat dui lacus luctus mauris hendrerit facilisis est nunc turpis pharetra eleifend duis porta platea nulla tortor aliquam est heading 4 lorem ipsum dolor sit amet odio tortor in sollicitudin phasellus interdum justo arcu hendrerit pretium nisi praesent tempus netus non neque blandit vel augue molestie cras fames vestibulum convallis facilisi hac imperdiet fermentum blandit phasellus nullam auctor elit enim eu mollis aliquet adipiscing feugiat dui lacus luctus mauris hendrerit facilisis est nunc turpis pharetra eleifend duis porta platea nulla tortor aliquam est links this is a link bulleted lists item 1 item 2 item nested 1 numbered lists item 1 item 2 item nested 1 todo list todo list item 1 todo list item 2 toggle items collapsibles this is a toggle item with collapsible text inside code from plone import api brains api content find portal_type wikipage for brain in brains print brain title tables header 1 header 2 different widths and borders merged cells and backgrounds blockquote this is a blockquote callouts this is a callout table of contents",
            result,
        )
