# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.interfaces import IDexterityItem
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.uuid.interfaces import IUUID
from zope.component import adapter
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
            id=u"doc1",
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
        class TestAdapter(object):
            order = 10
            block_type = "test"

            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self, value):
                self.context._handler_called = True

                value["value"] = u"changed: {}".format(value["value"])

                return value

        provideSubscriptionAdapter(
            TestAdapter,
            (IDexterityItem, IBrowserRequest),
        )

        self.deserialize(blocks={"123": {"@type": "test", "value": u"text"}})

        assert self.portal.doc1._handler_called is True
        assert self.portal.doc1.blocks["123"]["value"] == u"changed: text"

    def test_disabled_deserializer(self):
        @implementer(IBlockFieldDeserializationTransformer)
        @adapter(IBlocks, IBrowserRequest)
        class TestAdapter(object):
            order = 10
            block_type = "test"
            disabled = True

            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self, value):
                self.context._handler_called = True

                value["value"] = u"changed: {}".format(value["value"])

                return value

        provideSubscriptionAdapter(
            TestAdapter,
            (IDexterityItem, IBrowserRequest),
        )

        self.deserialize(blocks={"123": {"@type": "test", "value": u"text"}})

        assert not getattr(self.portal.doc1, "_handler_called", False)
        assert self.portal.doc1.blocks["123"]["value"] == u"text"

    def test_register_multiple_transform(self):
        @implementer(IBlockFieldDeserializationTransformer)
        @adapter(IBlocks, IBrowserRequest)
        class TestAdapterA(object):
            order = 10
            block_type = "test_multi"

            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self, value):
                self.context._handler_called_a = True

                value["value"] = value["value"].replace(u"a", u"b")

                return value

        @implementer(IBlockFieldDeserializationTransformer)
        @adapter(IBlocks, IBrowserRequest)
        class TestAdapterB(object):
            order = 11
            block_type = "test_multi"

            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self, value):
                self.context._handler_called_b = True

                value["value"] = value["value"].replace(u"b", u"c")

                return value

        provideSubscriptionAdapter(
            TestAdapterB,
            (IDexterityItem, IBrowserRequest),
        )

        provideSubscriptionAdapter(
            TestAdapterA,
            (IDexterityItem, IBrowserRequest),
        )

        self.deserialize(blocks={"123": {"@type": "test_multi", "value": u"a"}})

        self.assertTrue(self.portal.doc1._handler_called_a)
        self.assertTrue(self.portal.doc1._handler_called_b)
        self.assertEqual(self.portal.doc1.blocks["123"]["value"], u"c")

    def test_blocks_html_cleanup(self):
        self.deserialize(
            blocks={
                "123": {
                    "@type": "html",
                    "html": u"<script>nasty</script><div>This stays</div>",
                }
            }
        )

        self.assertEqual(
            self.portal.doc1.blocks["123"]["html"], u"<div>This stays</div>"
        )

    def test_blocks_image_resolve2uid(self):
        image_uid = IUUID(self.image)
        self.deserialize(
            blocks={"123": {"@type": "image", "url": self.image.absolute_url()}}
        )

        self.assertEqual(
            self.portal.doc1.blocks["123"]["url"], "../resolveuid/{}".format(image_uid)
        )

    def test_blocks_image_href(self):
        self.deserialize(
            blocks={"123": {"@type": "image", "url": "http://example.com/1.jpg"}}
        )

        self.assertEqual(
            self.portal.doc1.blocks["123"]["url"], "http://example.com/1.jpg"
        )

    def test_blocks_custom_block_resolve_standard_fields(self):
        self.deserialize(
            blocks={"123": {"@type": "foo", "url": self.portal.doc1.absolute_url()}}
        )
        doc_uid = IUUID(self.portal.doc1)

        self.assertEqual(
            self.portal.doc1.blocks["123"]["url"], "../resolveuid/{}".format(doc_uid)
        )

        self.deserialize(
            blocks={"123": {"@type": "foo", "href": self.portal.doc1.absolute_url()}}
        )
        doc_uid = IUUID(self.portal.doc1)

        self.assertEqual(
            self.portal.doc1.blocks["123"]["href"], "../resolveuid/{}".format(doc_uid)
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
            "../resolveuid/{}".format(doc_uid),
        )

    def test_deserialize_blocks_smart_href_array(self):
        self.deserialize(
            blocks={"123": {"@type": "foo", "href": [self.portal.doc1.absolute_url()]}}
        )
        doc_uid = IUUID(self.portal.doc1)

        self.assertEqual(
            self.portal.doc1.blocks["123"]["href"][0],
            "../resolveuid/{}".format(doc_uid),
        )
