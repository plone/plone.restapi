# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.component import queryUtility
from zope.lifecycleevent import modified

import unittest


class TestBlocksTransformer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("volto.blocks")
        fti.behaviors = tuple(behavior_list)

    def test_blocks_html_cleanup(self):
        doc = createContentInContainer(
            self.portal, u"Document", id=u"doc", title=u"A document",
            blocks={
                '123': {'@type': 'html', 'html':
                        u'<script>nasty</script><div>This stays</div>'}
            }
        )

        assert doc.blocks['123']['html'] == u'<div>This stays</div>'

        doc.blocks = {
            '123': {'@type': 'html', 'html':
                    u'<script>nasty</script><div>This '
                    u'stays</div><script>Still removed</script>'}
        }
        modified(doc)
        assert doc.blocks['123']['html'] == u'<div>This stays</div>'
