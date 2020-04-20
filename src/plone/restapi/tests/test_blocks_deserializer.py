# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.lifecycleevent import modified

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

    def test_blocks_html_cleanup(self):
        self.deserialize(blocks={
            '123': {'@type': 'html', 'html':
                    u'<script>nasty</script><div>This stays</div>'}
        })

        assert self.portal.doc1.blocks['123']['html'] == \
            u'<div>This stays</div>'
