# -*- coding: utf-8 -*-
# from plone import api
# from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISlotStorage
from plone.restapi.slots import Slot
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.component import getMultiAdapter

import unittest


class TestSerializeUserToJsonAdapters(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.make_content()

    def serialize(self, context, slot):
        serializer = getMultiAdapter((context, slot, self.request), ISerializeToJson)
        return serializer()

    def make_content(self):
        self.documents = createContentInContainer(
            self.portal, u"Folder", id=u"documents", title=u"Documents"
        )
        self.company = createContentInContainer(
            self.documents, u"Folder", id=u"company-a", title=u"Documents"
        )
        self.doc = createContentInContainer(
            self.company, u"Document", id=u"doc-1", title=u"Doc 1"
        )

    def test_serialize_slots_storage_empty(self):
        storage = ISlotStorage(self.portal)
        storage['left'] = Slot()

        res = self.serialize(self.portal, storage['left'])
        self.assertEqual(res, {
            '@id': 'http://nohost/plone/@slots/left',
            'slot_blocks': {},
            'slot_blocks_layout': {'items': []}
        })
