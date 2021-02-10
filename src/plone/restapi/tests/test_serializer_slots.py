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

    def serialize(self, context, slot_or_storage):
        serializer = getMultiAdapter(
            (context, slot_or_storage, self.request), ISerializeToJson)
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

    def test_slot_empty(self):
        storage = ISlotStorage(self.portal)
        storage['left'] = Slot()

        res = self.serialize(self.portal, storage['left'])
        self.assertEqual(res, {
            '@id': 'http://nohost/plone/@slots/left',
            'blocks': {},
            'blocks_layout': {'items': []}
        })

    def test_slot(self):
        storage = ISlotStorage(self.portal)
        storage['left'] = Slot(**({
            'blocks': {1: {}, 2: {}, 3: {}, },
            'blocks_layout': {'items': [1, 2, 3]}
        }))

        res = self.serialize(self.portal, storage['left'])
        self.assertEqual(res, {
            '@id': 'http://nohost/plone/@slots/left',
            'blocks_layout': {'items': [1, 2, 3]},
            'blocks': {1: {}, 2: {}, 3: {}}
        })

    def test_slot_deep(self):
        rootstore = ISlotStorage(self.portal)
        rootstore['left'] = Slot(**({
            'blocks': {1: {}, 2: {}, 3: {}, },
            'blocks_layout': {'items': [1, 2, 3]}
        }))

        storage = ISlotStorage(self.doc)
        storage['left'] = Slot()
        res = self.serialize(self.doc, storage['left'])
        self.assertEqual(res, {
            '@id': 'http://nohost/plone/documents/company-a/doc-1/@slots/left',
            'blocks': {1: {u'_v_inherit': True},
                            2: {u'_v_inherit': True},
                            3: {u'_v_inherit': True}},
            'blocks_layout': {'items': [1, 2, 3]}})

    def test_data_override_with_isVariant(self):
        rootstore = ISlotStorage(self.portal)
        rootstore['left'] = Slot(**({
            'blocks': {
                1: {'title': 'First'},
                3: {'title': 'Third'},
            },
            'blocks_layout': {'items': [1, 3]}
        }))

        storage = ISlotStorage(self.doc)
        storage['left'] = Slot(
            blocks={2: {'s:isVariantOf': 1, 'title': 'Second'}},
            blocks_layout={'items': [2]},
        )
        res = self.serialize(self.doc, storage['left'])
        self.assertEqual(res, {
            '@id': 'http://nohost/plone/documents/company-a/doc-1/@slots/left',
            'blocks': {2: {u's:isVariantOf': 1, u'title': u'Second'},
                            3: {u'_v_inherit': True, u'title': u'Third'}},
            'blocks_layout': {'items': [2, 3]}})

    def test_change_order_from_layout(self):
        rootstore = ISlotStorage(self.portal)
        rootstore['left'] = Slot(**({
            'blocks': {
                1: {'title': 'First'},
                3: {'title': 'Third'},
                5: {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [5, 1, 3]}
        }))

        storage = ISlotStorage(self.doc)
        storage['left'] = Slot(
            blocks={2: {'s:isVariantOf': 1, 'title': 'Second'}},
            blocks_layout={'items': [3, 2]},
        )
        res = self.serialize(self.doc, storage['left'])
        self.assertEqual(res, {
            '@id': 'http://nohost/plone/documents/company-a/doc-1/@slots/left',
            'blocks': {2: {u's:isVariantOf': 1, u'title': u'Second'},
                            3: {u'_v_inherit': True, u'title': u'Third'},
                            5: {u'_v_inherit': True, u'title': u'Fifth'}},
            'blocks_layout': {'items': [3, 2, 5]}})

    def test_serialize_storage(self):
        rootstore = ISlotStorage(self.portal)
        rootstore['left'] = Slot(**({
            'blocks': {
                1: {'title': 'First'},
                3: {'title': 'Third'},
                5: {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [5, 1, 3]}
        }))
        rootstore['right'] = Slot(**({
            'blocks': {
                6: {'title': 'First'},
                7: {'title': 'Third'},
                8: {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [8, 6, 7]}
        }))

        storage = ISlotStorage(self.doc)
        storage['left'] = Slot(
            blocks={2: {'s:isVariantOf': 1, 'title': 'Second'}},
            blocks_layout={'items': [3, 2]},
        )

        res = self.serialize(self.doc, storage)
        self.assertEqual(res, {
            '@id': 'http://nohost/plone/documents/company-a/doc-1/@slots',
            'items': {
                u'left': {
                    '@id': 'http://nohost/plone/documents/company-a/doc-1/@slots/left',
                    'blocks': {
                        2: {u's:isVariantOf': 1, u'title': u'Second'},
                        3: {u'_v_inherit': True, u'title': u'Third'},
                        5: {u'_v_inherit': True, u'title': u'Fifth'}
                    },
                    'blocks_layout': {'items': [3, 2, 5]}},
                u'right': {
                    '@id': 'http://nohost/plone/documents/company-a/doc-1/@slots/right',
                           'blocks': {
                               6: {u'title': u'First', u'_v_inherit': True},
                               7: {u'title': u'Third', u'_v_inherit': True},
                               8: {u'title': u'Fifth', u'_v_inherit': True}
                           },
                    'blocks_layout': {'items': [8, 6, 7]}}}})
