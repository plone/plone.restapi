from importlib import import_module
from plone.app.testing import logout
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.interfaces import IDexterityItem
from plone.dexterity.utils import iterSchemata
from plone.namedfile.file import NamedBlobImage
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from z3c.form.interfaces import IDataManager
from zope.component import adapter
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import provideSubscriptionAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import pathlib
import unittest


HAS_PLONE_6 = getattr(
    import_module("Products.CMFPlone.factory"), "PLONE60MARKER", False
)
IMAGE_PATH = (pathlib.Path(__file__).parent / "image.png").resolve()
IMAGE_DATA = IMAGE_PATH.read_bytes()


class TestBlocksSerializer(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("volto.blocks")
        fti.behaviors = tuple(behavior_list)

        self.portal.invokeFactory("Document", id="doc1")
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(self.portal.doc1, "publish")
        self.image = self.portal[
            self.portal.invokeFactory("Image", id="image-1", title="Target image")
        ]
        self.image.image = NamedBlobImage(data=IMAGE_DATA, filename="test.jpg")
        self.image.reindexObject()

    def serialize(self, context, blocks):
        fieldname = "blocks"
        field = None
        for schema in iterSchemata(context):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        if field is None:
            raise ValueError("blocks field not in the schema of %s" % context)
        dm = getMultiAdapter((context, field), IDataManager)
        dm.set(blocks)
        serializer = getMultiAdapter((field, context, self.request), IFieldSerializer)
        return serializer()

    def test_register_serializer(self):
        @adapter(IBlocks, IBrowserRequest)
        @implementer(IBlockFieldSerializationTransformer)
        class TestAdapterA:
            order = 10
            block_type = "test_multi"

            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self, value):
                self.context._handler_called_a = True

                value["value"] = value["value"].replace("a", "b")

                return value

        @adapter(IBlocks, IBrowserRequest)
        @implementer(IBlockFieldSerializationTransformer)
        class TestAdapterB:
            order = 11
            block_type = "test_multi"

            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self, value):
                self.context._handler_called_b = True

                value["value"] = value["value"].replace("b", "c")

                return value

        provideSubscriptionAdapter(TestAdapterA, (IDexterityItem, IBrowserRequest))
        provideSubscriptionAdapter(TestAdapterB, (IDexterityItem, IBrowserRequest))
        value = self.serialize(
            context=self.portal.doc1,
            blocks={"123": {"@type": "test_multi", "value": "a"}},
        )
        self.assertEqual(value["123"]["value"], "c")

        sm = getGlobalSiteManager()
        sm.adapters.unsubscribe(
            (IDexterityItem, IBrowserRequest),
            IBlockFieldSerializationTransformer,
            TestAdapterA,
        )
        sm.adapters.unsubscribe(
            (IDexterityItem, IBrowserRequest),
            IBlockFieldSerializationTransformer,
            TestAdapterB,
        )

    def test_disabled_serializer(self):
        @implementer(IBlockFieldSerializationTransformer)
        @adapter(IBlocks, IBrowserRequest)
        class TestAdapter:
            order = 10
            block_type = "test"
            disabled = True

            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self, value):
                self.context._handler_called = True

                value["value"] = "changed: {}".format(value["value"])

                return value

        provideSubscriptionAdapter(
            TestAdapter,
            (IDexterityItem, IBrowserRequest),
        )
        value = self.serialize(
            context=self.portal.doc1,
            blocks={"123": {"@type": "test", "value": "text"}},
        )

        assert not getattr(self.portal.doc1, "_handler_called", False)
        self.assertEqual(value["123"]["value"], "text")

        sm = getGlobalSiteManager()
        sm.adapters.unsubscribe(
            (IDexterityItem, IBrowserRequest),
            IBlockFieldSerializationTransformer,
            TestAdapter,
        )

    def test_serialize_blocks_smart_href_array_volto_object_browser(self):
        doc_uid = IUUID(self.portal.doc1)
        value = self.serialize(
            context=self.portal.doc1,
            blocks={
                "123": {
                    "@type": "foo",
                    "href": [{"@id": f"../resolveuid/{doc_uid}"}],
                }
            },
        )

        self.assertEqual(
            value["123"]["href"][0]["@id"], self.portal.doc1.absolute_url()
        )

    def test_serialize_blocks_smart_href_array(self):
        doc_uid = IUUID(self.portal.doc1)
        value = self.serialize(
            context=self.portal.doc1,
            blocks={"123": {"@type": "foo", "href": [f"../resolveuid/{doc_uid}"]}},
        )

        self.assertEqual(value["123"]["href"][0], self.portal.doc1.absolute_url())

    def test_serialize_subblocks_transformers(self):
        # use the href smart field transformer for testing subblocks transformers
        doc_uid = IUUID(self.portal.doc1)
        subblock = {"@type": "foo", "href": [f"../resolveuid/{doc_uid}"]}
        value = self.serialize(
            context=self.portal.doc1,
            blocks={
                "1": {
                    "@type": "columns_block",
                    "data": {
                        "blocks": {"2": {"@type": "tabs", "blocks": {"3": subblock}}}
                    },
                }
            },
        )

        href = value["1"]["data"]["blocks"]["2"]["blocks"]["3"]["href"]

        self.assertEqual(href[0], self.portal.doc1.absolute_url())

    def test_internal_link_serializer(self):
        doc_uid = IUUID(self.portal["doc1"])
        resolve_uid_link = {
            "@id": f"../resolveuid/{doc_uid}",
            "title": "Welcome to Plone",
        }
        blocks = {
            "2caef9e6-93ff-4edf-896f-8c16654a9923": {
                "@type": "slate",
                "plaintext": "this is a slate link inside some text",
                "value": [
                    {
                        "children": [
                            {"text": "this is a "},
                            {
                                "children": [
                                    {"text": ""},
                                    {
                                        "children": [{"text": "slate link"}],
                                        "data": {
                                            "link": {
                                                "internal": {
                                                    "internal_link": [resolve_uid_link]
                                                }
                                            }
                                        },
                                        "type": "a",
                                    },
                                    {"text": ""},
                                ],
                                "type": "strong",
                            },
                            {"text": " inside some text"},
                        ],
                        "type": "p",
                    }
                ],
            },
            "6b2be2e6-9857-4bcc-a21a-29c0449e1c68": {"@type": "title"},
        }

        res = self.serialize(
            context=self.portal["doc1"],
            blocks=blocks,
        )

        value = res["2caef9e6-93ff-4edf-896f-8c16654a9923"]["value"]
        link = value[0]["children"][1]["children"][1]
        resolve_link = link["data"]["link"]["internal"]["internal_link"][0]["@id"]

        self.assertTrue(resolve_link == self.portal.absolute_url() + "/doc1")

    def test_simple_link_serializer(self):
        doc_uid = IUUID(self.portal["doc1"])
        resolve_uid_link = f"../resolveuid/{doc_uid}"

        blocks = {
            "abc": {
                "@type": "slate",
                "plaintext": "Frontpage content here",
                "value": [
                    {
                        "children": [
                            {"text": "Frontpage "},
                            {
                                "children": [{"text": "content "}],
                                "data": {
                                    "url": resolve_uid_link,
                                },
                                "type": "link",
                            },
                            {"text": "here"},
                        ],
                        "type": "h2",
                    }
                ],
            }
        }
        res = self.serialize(
            context=self.portal["doc1"],
            blocks=blocks,
        )
        value = res["abc"]["value"]
        link = value[0]["children"][1]["data"]["url"]
        self.assertEqual(link, self.portal.absolute_url() + "/doc1")

    def test_simple_link_serializer_with_anchor(self):
        doc_uid = IUUID(self.portal["doc1"])
        resolve_uid_link = f"../resolveuid/{doc_uid}#anchor-id"

        blocks = {
            "abc": {
                "@type": "slate",
                "plaintext": "Frontpage content here",
                "value": [
                    {
                        "children": [
                            {"text": "Frontpage "},
                            {
                                "children": [{"text": "content "}],
                                "data": {
                                    "url": resolve_uid_link,
                                },
                                "type": "link",
                            },
                            {"text": "here"},
                        ],
                        "type": "h2",
                    }
                ],
            }
        }
        res = self.serialize(
            context=self.portal["doc1"],
            blocks=blocks,
        )
        value = res["abc"]["value"]
        link = value[0]["children"][1]["data"]["url"]
        self.assertEqual(link, f"{self.portal['doc1'].absolute_url()}#anchor-id")

    def test_simple_link_serializer_with_suffix(self):
        doc_uid = IUUID(self.portal["doc1"])
        resolve_uid_link = f"../resolveuid/{doc_uid}/@@download/file"

        blocks = {
            "abc": {
                "@type": "slate",
                "plaintext": "Frontpage content here",
                "value": [
                    {
                        "children": [
                            {"text": "Frontpage "},
                            {
                                "children": [{"text": "content "}],
                                "data": {
                                    "url": resolve_uid_link,
                                },
                                "type": "link",
                            },
                            {"text": "here"},
                        ],
                        "type": "h2",
                    }
                ],
            }
        }
        res = self.serialize(
            context=self.portal["doc1"],
            blocks=blocks,
        )
        value = res["abc"]["value"]
        link = value[0]["children"][1]["data"]["url"]
        self.assertEqual(link, f"{self.portal['doc1'].absolute_url()}/@@download/file")

    def test_simple_link_serializer_with_suffix_and_anchor(self):
        doc_uid = IUUID(self.portal["doc1"])
        resolve_uid_link = f"../resolveuid/{doc_uid}/@@download/file#anchor-id"

        blocks = {
            "abc": {
                "@type": "slate",
                "plaintext": "Frontpage content here",
                "value": [
                    {
                        "children": [
                            {"text": "Frontpage "},
                            {
                                "children": [{"text": "content "}],
                                "data": {
                                    "url": resolve_uid_link,
                                },
                                "type": "link",
                            },
                            {"text": "here"},
                        ],
                        "type": "h2",
                    }
                ],
            }
        }
        res = self.serialize(
            context=self.portal["doc1"],
            blocks=blocks,
        )
        value = res["abc"]["value"]
        link = value[0]["children"][1]["data"]["url"]
        self.assertEqual(
            link, f"{self.portal['doc1'].absolute_url()}/@@download/file#anchor-id"
        )

    def test_slate_table_block_link_serializer(self):
        doc_uid = IUUID(self.portal["doc1"])
        resolve_uid_link = f"../resolveuid/{doc_uid}"
        blocks = {
            "abc": {
                "@type": "slateTable",
                "table": {
                    "hideHeaders": False,
                    "fixed": True,
                    "compact": False,
                    "basic": False,
                    "celled": True,
                    "inverted": False,
                    "striped": False,
                    "rows": [
                        {
                            "key": "25k7t",
                            "cells": [
                                {
                                    "key": "ajes8",
                                    "type": "header",
                                    "value": [
                                        {
                                            "type": "p",
                                            "children": [{"text": "Table with links"}],
                                        }
                                    ],
                                },
                                {
                                    "key": "cm2bj",
                                    "type": "header",
                                    "value": [
                                        {
                                            "type": "p",
                                            "children": [{"text": "Table with links"}],
                                        }
                                    ],
                                },
                            ],
                        },
                        {
                            "key": "6gteb",
                            "cells": [
                                {
                                    "key": "1gs74",
                                    "type": "data",
                                    "value": [
                                        {
                                            "type": "p",
                                            "children": [
                                                {"text": ""},
                                                {
                                                    "type": "link",
                                                    "data": {"url": resolve_uid_link},
                                                    "children": [
                                                        {
                                                            "text": (
                                                                "This internal" " link"
                                                            )
                                                        }
                                                    ],
                                                },
                                                {"text": ""},
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "key": "ab93b",
                                    "type": "data",
                                    "value": [
                                        {
                                            "type": "p",
                                            "children": [
                                                {"text": "This "},
                                                {
                                                    "type": "link",
                                                    "data": {
                                                        "url": "https://google.com/"
                                                    },
                                                    "children": [{"text": "external"}],
                                                },
                                                {"text": " link"},
                                            ],
                                        }
                                    ],
                                },
                            ],
                        },
                    ],
                },
            }
        }

        res = self.serialize(
            context=self.portal["doc1"],
            blocks=blocks,
        )
        rows = res["abc"]["table"]["rows"]
        cell = rows[1]["cells"][0]
        link = cell["value"][0]["children"][1]["data"]["url"]
        self.assertEqual(link, self.portal.absolute_url() + "/doc1")

    @unittest.skipUnless(
        HAS_PLONE_6,
        "image_scales were added to the catalog in Plone 6",
    )
    def test_image_scales_serializer(self):
        image_uid = self.image.UID()
        res = self.serialize(
            context=self.portal["doc1"],
            blocks={"123": {"@type": "image", "url": f"../resolveuid/{image_uid}"}},
        )
        self.assertEqual(res["123"]["url"], self.image.absolute_url())
        self.assertIn("image_scales", res["123"])

    @unittest.skipUnless(
        HAS_PLONE_6,
        "image_scales were added to the catalog in Plone 6",
    )
    def test_image_scales_serializer_is_json_compatible(self):
        image_uid = self.image.UID()
        res = self.serialize(
            context=self.portal["doc1"],
            blocks={"123": {"@type": "image", "url": f"../resolveuid/{image_uid}"}},
        )
        self.assertIs(type(res["123"]["image_scales"]), dict)

    def test_teaser_block_serializer_dynamic(self):
        doc = self.portal["doc1"]
        doc_uid = doc.UID()
        resolve_uid_link = f"../resolveuid/{doc_uid}"
        value = self.serialize(
            context=self.portal.doc1,
            blocks={
                "1": {
                    "@type": "teaser",
                    "href": resolve_uid_link,
                    "overwrite": False,
                }
            },
        )

        block = value["1"]
        self.assertEqual(block["title"], doc.title)
        self.assertEqual(block["description"], doc.description)
        href = block["href"][0]
        self.assertEqual(href["@id"], doc.absolute_url())

    def test_teaser_block_serializer_dynamic_private(self):
        # if user doesn't have permission to view the target,
        # don't reveal its data
        doc = self.portal.doc1
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(doc, "retract")
        doc_uid = doc.UID()
        resolve_uid_link = f"../resolveuid/{doc_uid}"
        logout()
        value = self.serialize(
            context=self.portal.doc1,
            blocks={
                "1": {
                    "@type": "teaser",
                    "href": resolve_uid_link,
                    "overwrite": False,
                }
            },
        )

        block = value["1"]
        self.assertEqual(block, {"@type": "teaser", "href": [], "overwrite": False})

    def test_teaser_block_serializer_dynamic_nested(self):
        doc = self.portal["doc1"]
        doc_uid = doc.UID()
        resolve_uid_link = f"../resolveuid/{doc_uid}"
        value = self.serialize(
            context=self.portal.doc1,
            blocks={
                "grid": {
                    "@type": "gridBlock",
                    "blocks": {
                        "1": {
                            "@type": "teaser",
                            "href": resolve_uid_link,
                            "overwrite": False,
                        },
                    },
                    "blocks_layout": {"items": ["1"]},
                }
            },
        )

        block = value["grid"]["blocks"]["1"]
        self.assertEqual(block["title"], doc.title)
        self.assertEqual(block["description"], doc.description)
        href = block["href"][0]
        self.assertEqual(href["@id"], doc.absolute_url())

    def test_teaser_block_serializer_with_overwrite(self):
        doc = self.portal["doc1"]
        doc_uid = doc.UID()
        resolve_uid_link = f"../resolveuid/{doc_uid}"
        value = self.serialize(
            context=self.portal.doc1,
            blocks={
                "1": {
                    "@type": "teaser",
                    "href": resolve_uid_link,
                    "overwrite": True,
                    "title": "Custom title",
                    "description": "Custom description",
                }
            },
        )

        block = value["1"]
        self.assertEqual(block["title"], "Custom title")
        self.assertEqual(block["description"], "Custom description")
        href = block["href"][0]
        self.assertEqual(href["@id"], doc.absolute_url())

    def test_teaser_block_serializer_legacy(self):
        # no "overwrite" key -> default to True
        doc = self.portal["doc1"]
        doc_uid = doc.UID()
        resolve_uid_link = f"../resolveuid/{doc_uid}"
        value = self.serialize(
            context=self.portal.doc1,
            blocks={
                "1": {
                    "@type": "teaser",
                    "href": [{"@id": resolve_uid_link}],
                    "title": "Custom title",
                    "description": "Custom description",
                }
            },
        )

        block = value["1"]
        self.assertEqual(block["title"], "Custom title")
        self.assertEqual(block["description"], "Custom description")
        href = block["href"][0]
        self.assertEqual(href["@id"], doc.absolute_url())
