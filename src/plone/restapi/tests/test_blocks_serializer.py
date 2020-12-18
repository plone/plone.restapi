# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.interfaces import IDexterityItem
from plone.dexterity.utils import iterSchemata
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from z3c.form.interfaces import IDataManager
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import provideSubscriptionAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import unittest


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

        self.portal.invokeFactory("Document", id=u"doc1")
        self.image = self.portal[
            self.portal.invokeFactory("Image", id="image-1", title="Target image")
        ]

    def serialize(self, context, blocks):
        fieldname = "blocks"
        for schema in iterSchemata(context):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        dm = getMultiAdapter((context, field), IDataManager)
        dm.set(blocks)
        serializer = getMultiAdapter((field, context, self.request), IFieldSerializer)
        return serializer()

    def test_register_serializer(self):
        @adapter(IBlocks, IBrowserRequest)
        @implementer(IBlockFieldSerializationTransformer)
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

        @adapter(IBlocks, IBrowserRequest)
        @implementer(IBlockFieldSerializationTransformer)
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

        provideSubscriptionAdapter(TestAdapterA, (IDexterityItem, IBrowserRequest))
        provideSubscriptionAdapter(TestAdapterB, (IDexterityItem, IBrowserRequest))
        value = self.serialize(
            context=self.portal.doc1,
            blocks={"123": {"@type": "test_multi", "value": u"a"}},
        )
        self.assertEqual(value["123"]["value"], u"c")

    def test_disabled_serializer(self):
        @implementer(IBlockFieldSerializationTransformer)
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
        value = self.serialize(
            context=self.portal.doc1,
            blocks={"123": {"@type": "test", "value": u"text"}},
        )

        assert not getattr(self.portal.doc1, "_handler_called", False)
        self.assertEqual(value["123"]["value"], u"text")
