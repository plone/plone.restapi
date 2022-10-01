from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.interfaces import IDexterityItem
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.uuid.interfaces import IUUID
from zope.component import adapter
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import provideSubscriptionAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import json
import unittest


class TestBlocksDeserializer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("volto.blocks")
        fti.behaviors = tuple(behavior_list)

        self.portal.invokeFactory(
            "Document",
            id="doc1",
        )
        self.image = self.portal[
            self.portal.invokeFactory("Image", id="image-1", title="Target image")
        ]

    def deserialize(self, blocks=None, validate_all=False, context=None):
        blocks = blocks or ""
        context = context or self.portal.doc1
        self.request["BODY"] = json.dumps({"blocks": blocks})
        deserializer = getMultiAdapter((context, self.request), IDeserializeFromJson)

        return deserializer(validate_all=validate_all)

    def test_register_deserializer(self):
        @implementer(IBlockFieldDeserializationTransformer)
        @adapter(IBlocks, IBrowserRequest)
        class TestAdapter:
            order = 10
            block_type = "test"

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

        self.deserialize(blocks={"123": {"@type": "test", "value": "text"}})

        assert self.portal.doc1._handler_called is True
        assert self.portal.doc1.blocks["123"]["value"] == "changed: text"

        sm = getGlobalSiteManager()
        sm.adapters.unsubscribe(
            (IDexterityItem, IBrowserRequest),
            IBlockFieldDeserializationTransformer,
            TestAdapter,
        )

    def test_disabled_deserializer(self):
        @implementer(IBlockFieldDeserializationTransformer)
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

        self.deserialize(blocks={"123": {"@type": "test", "value": "text"}})

        assert not getattr(self.portal.doc1, "_handler_called", False)
        assert self.portal.doc1.blocks["123"]["value"] == "text"

        sm = getGlobalSiteManager()
        sm.adapters.unsubscribe(
            (IDexterityItem, IBrowserRequest),
            IBlockFieldDeserializationTransformer,
            TestAdapter,
        )

    def test_register_multiple_transform(self):
        @implementer(IBlockFieldDeserializationTransformer)
        @adapter(IBlocks, IBrowserRequest)
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

        @implementer(IBlockFieldDeserializationTransformer)
        @adapter(IBlocks, IBrowserRequest)
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

        provideSubscriptionAdapter(
            TestAdapterB,
            (IDexterityItem, IBrowserRequest),
        )

        provideSubscriptionAdapter(
            TestAdapterA,
            (IDexterityItem, IBrowserRequest),
        )

        self.deserialize(blocks={"123": {"@type": "test_multi", "value": "a"}})

        self.assertTrue(self.portal.doc1._handler_called_a)
        self.assertTrue(self.portal.doc1._handler_called_b)
        self.assertEqual(self.portal.doc1.blocks["123"]["value"], "c")

        sm = getGlobalSiteManager()
        sm.adapters.unsubscribe(
            (IDexterityItem, IBrowserRequest),
            IBlockFieldDeserializationTransformer,
            TestAdapterA,
        )
        sm.adapters.unsubscribe(
            (IDexterityItem, IBrowserRequest),
            IBlockFieldDeserializationTransformer,
            TestAdapterB,
        )

    def test_blocks_html_cleanup(self):
        self.deserialize(
            blocks={
                "123": {
                    "@type": "html",
                    "html": "<script>nasty</script><div>This stays</div>",
                }
            }
        )

        self.assertEqual(
            self.portal.doc1.blocks["123"]["html"], "<div>This stays</div>"
        )

    def test_blocks_image_resolve2uid(self):
        image_uid = IUUID(self.image)
        self.deserialize(
            blocks={"123": {"@type": "image", "url": self.image.absolute_url()}}
        )

        self.assertEqual(
            self.portal.doc1.blocks["123"]["url"], f"../resolveuid/{image_uid}"
        )

    def test_blocks_image_href(self):
        self.deserialize(
            blocks={"123": {"@type": "image", "url": "http://example.com/1.jpg"}}
        )

        self.assertEqual(
            self.portal.doc1.blocks["123"]["url"], "http://example.com/1.jpg"
        )

    def test_blocks_doc_relative(self):
        doc_uid = IUUID(self.portal.doc1)
        self.deserialize(blocks={"123": {"@type": "foo", "url": "/doc1"}})

        self.assertEqual(
            self.portal.doc1.blocks["123"]["url"], f"../resolveuid/{doc_uid}"
        )

    def test_blocks_image_relative(self):
        image_uid = IUUID(self.image)
        self.deserialize(blocks={"123": {"@type": "image", "url": "/image-1"}})

        self.assertEqual(
            self.portal.doc1.blocks["123"]["url"], f"../resolveuid/{image_uid}"
        )

    def test_blocks_custom_block_resolve_standard_fields(self):
        self.deserialize(
            blocks={"123": {"@type": "foo", "url": self.portal.doc1.absolute_url()}}
        )
        doc_uid = IUUID(self.portal.doc1)

        self.assertEqual(
            self.portal.doc1.blocks["123"]["url"], f"../resolveuid/{doc_uid}"
        )

        self.deserialize(
            blocks={"123": {"@type": "foo", "href": self.portal.doc1.absolute_url()}}
        )
        doc_uid = IUUID(self.portal.doc1)

        self.assertEqual(
            self.portal.doc1.blocks["123"]["href"], f"../resolveuid/{doc_uid}"
        )

    def test_blocks_custom_block_doesnt_resolve_non_standard_fields(self):
        self.deserialize(
            blocks={"123": {"@type": "foo", "link": self.portal.doc1.absolute_url()}}
        )

        self.assertEqual(
            self.portal.doc1.blocks["123"]["link"], self.portal.doc1.absolute_url()
        )

    def test_deserialize_blocks_smart_href_array_volto_object_browser(self):
        self.deserialize(
            blocks={
                "123": {
                    "@type": "foo",
                    "href": [{"@id": self.portal.doc1.absolute_url()}],
                }
            }
        )
        doc_uid = IUUID(self.portal.doc1)

        self.assertEqual(
            self.portal.doc1.blocks["123"]["href"][0]["@id"],
            f"../resolveuid/{doc_uid}",
        )

    def test_deserialize_blocks_smart_href_array(self):
        self.deserialize(
            blocks={"123": {"@type": "foo", "href": [self.portal.doc1.absolute_url()]}}
        )
        doc_uid = IUUID(self.portal.doc1)

        self.assertEqual(
            self.portal.doc1.blocks["123"]["href"][0],
            f"../resolveuid/{doc_uid}",
        )

    def test_deserialize_subblocks_transformers(self):
        # use the html transformer to test subblocks transformers
        subblock = {
            "@type": "html",
            "html": "<script>nasty</script><div>This stays</div>",
        }
        self.deserialize(
            blocks={
                "1": {
                    "@type": "columns_block",
                    "data": {
                        "blocks": {"2": {"@type": "tabs", "blocks": {"3": subblock}}}
                    },
                }
            }
        )

        block = self.portal.doc1.blocks["1"]["data"]["blocks"]["2"]["blocks"]["3"][
            "html"
        ]
        self.assertEqual(block, "<div>This stays</div>")

    def test_slate_internal_link_deserializer(self):
        blocks = {
            "2caef9e6-93ff-4edf-896f-8c16654a9923": {
                "@type": "slate",
                "plaintext": "this is a slate link inside some text",
                "value": [
                    {
                        "type": "p",
                        "children": [
                            {"text": "this is a "},
                            {
                                "children": [
                                    {"text": ""},
                                    {
                                        "type": "a",
                                        "children": [{"text": "slate link"}],
                                        "data": {
                                            "link": {
                                                "internal": {
                                                    "internal_link": [
                                                        {
                                                            "@id": "%s/image-1"
                                                            % self.portal.absolute_url(),
                                                            "title": "Image 1",
                                                        }
                                                    ]
                                                }
                                            }
                                        },
                                    },
                                    {"text": ""},
                                ],
                                "type": "strong",
                            },
                            {"text": " inside some text"},
                        ],
                    }
                ],
            },
            "6b2be2e6-9857-4bcc-a21a-29c0449e1c68": {"@type": "title"},
        }
        res = self.deserialize(blocks=blocks)
        value = res.blocks["2caef9e6-93ff-4edf-896f-8c16654a9923"]["value"]
        link = value[0]["children"][1]["children"][1]
        resolve_link = link["data"]["link"]["internal"]["internal_link"][0]["@id"]
        self.assertTrue(resolve_link.startswith("../resolveuid/"))

    def test_slate_simple_link_deserializer(self):
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
                                    "url": "%s/image-1" % self.portal.absolute_url()
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

        res = self.deserialize(blocks=blocks)
        value = res.blocks["abc"]["value"]
        link = value[0]["children"][1]["data"]["url"]
        self.assertTrue(link.startswith("../resolveuid/"))

    def test_aquisition_messing_with_link_deserializer(self):
        self.portal.invokeFactory(
            "Folder",
            id="aktuelles",
        )
        self.portal["aktuelles"].invokeFactory(
            "Document",
            id="meldungen",
        )
        self.portal.invokeFactory(
            "Folder",
            id="institut",
        )

        wrong_uid = IUUID(self.portal["aktuelles"]["meldungen"])

        self.deserialize(
            blocks={
                "123": {
                    "@type": "foo",
                    "href": [
                        {
                            # Pointing to a not created yet object, but matches because acquisition
                            # with another existing parent content with alike-ish path structure
                            "@id": f"{self.portal.absolute_url()}/institut/aktuelles/meldungen"
                        }
                    ],
                }
            }
        )
        self.assertNotEqual(
            self.portal.doc1.blocks["123"]["href"][0]["@id"],
            f"../resolveuid/{wrong_uid}",
        )

        # another use-case: pass "../.." as link. Do not change the link.
        self.deserialize(
            blocks={
                "123": {
                    "@type": "foo",
                    "href": [
                        {
                            # Pointing to a not created yet object, but matches because acquisition
                            # with another existing parent content with alike-ish path structure
                            "@id": "../.."
                        }
                    ],
                }
            }
        )
        self.assertEqual(
            self.portal.doc1.blocks["123"]["href"][0]["@id"],
            "../..",
        )
