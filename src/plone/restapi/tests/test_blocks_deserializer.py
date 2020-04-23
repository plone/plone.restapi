# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.interfaces import IDexterityItem
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockConverter
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import provideAdapter
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

        self.portal.invokeFactory("Document", id=u"doc1",)

    def deserialize(self, blocks=None, validate_all=False, context=None):
        blocks = blocks or ''
        context = context or self.portal.doc1
        self.request["BODY"] = json.dumps({'blocks': blocks})
        deserializer = getMultiAdapter(
            (context, self.request), IDeserializeFromJson)

        return deserializer(validate_all=validate_all)

    def test_register_deserializer(self):

        @implementer(IBlockConverter)
        @adapter(IBlocks, IBrowserRequest)
        class TestAdapter(object):
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self, value):
                self.context._handler_called = True

                value['value'] = u"changed: {}".format(value['value'])

                return value

        provideAdapter(TestAdapter, (IDexterityItem, IBrowserRequest),
                       name="test_adapter")

        self.deserialize(blocks={
            '123': {'@type': 'test_adapter', 'value': u'text'}
        })

        assert self.portal.doc1._handler_called is True
        assert self.portal.doc1.blocks['123']['value'] == u'changed: text'

    def test_blocks_html_cleanup(self):
        self.deserialize(blocks={
            '123': {'@type': 'html', 'html':
                    u'<script>nasty</script><div>This stays</div>'}
        })

        assert self.portal.doc1.blocks['123']['html'] == \
            u'<div>This stays</div>'
