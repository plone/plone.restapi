# -*- coding: utf-8 -*-

from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.slots import Slot
from plone.restapi.slots.interfaces import ISlots
from plone.restapi.slots.interfaces import ISlotStorage
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from zope.component import getMultiAdapter


class TestSlotsEngineIntegration(PloneTestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.portal.acl_users.userFolderAddUser(
            'simple_member', 'slots_pw', ["Member"], []
        )

        self.portal.acl_users.userFolderAddUser(
            'editor_member', 'slots_pw', ["Editor"], []
        )

        self.make_content()

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

    def test_deserialize_empty(self):
        storage = ISlotStorage(self.doc)
        deserializer = getMultiAdapter(
            (self.doc, storage, self.request), IDeserializeFromJson)
        deserializer()

        self.assertEqual(list(storage.keys()), [])

    def test_deserialize_put_some(self):
        storage = ISlotStorage(self.doc)

        deserializer = getMultiAdapter(
            (self.doc, storage, self.request), IDeserializeFromJson)

        deserializer({
            "left": {
                'blocks_layout': {'items': [u'3', u'2', u'5', u'4']},
                'blocks': {
                    u'2': {'title': 'Second', 's:isVariantOf': u'1'},
                    u'3': {'title': 'Third', '_v_inherit': True},
                    u'5': {'title': 'Fifth', '_v_inherit': True},
                },
            },
            "right": {
                'blocks_layout': {'items': [u'6', u'7']},
                'blocks': {
                    u'6': {'title': 'Sixth'},
                }
            }
        })

        self.assertEqual(list(storage.keys()), ['left', 'right'])
        self.assertEqual(storage['left'].blocks,
                         {u'2': {'title': 'Second', 's:isVariantOf': u'1'}, })
        self.assertEqual(storage['left'].blocks_layout, {"items": [u'2']})

        self.assertEqual(storage['right'].blocks,
                         {u'6': {'title': 'Sixth'}, })
        self.assertEqual(storage['right'].blocks_layout, {"items": [u'6']})

    def test_delete_all_with_dict(self):
        storage = ISlotStorage(self.doc)

        storage['left'] = Slot(**({
            'blocks': {
                u'1': {'title': 'First'},
                u'3': {'title': 'Third'},
                u'5': {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [u'5', u'1', u'3']}
        }))
        storage['right'] = Slot(**({
            'blocks': {
                u'6': {'title': 'First'},
                u'7': {'title': 'Third'},
                u'8': {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [u'8', u'6', u'7']}
        }))

        deserializer = getMultiAdapter(
            (self.doc, storage, self.request), IDeserializeFromJson)
        deserializer({'left': {}, 'right': {}})

        left = storage['left']
        self.assertEqual(left.blocks, {})
        self.assertEqual(left.blocks_layout, {"items": []})

    def test_delete_all_with_empty(self):
        storage = ISlotStorage(self.doc)

        storage['left'] = Slot(**({
            'blocks': {
                u'1': {'title': 'First'},
                u'3': {'title': 'Third'},
                u'5': {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [u'5', u'1', u'3']}
        }))
        storage['right'] = Slot(**({
            'blocks': {
                u'6': {'title': 'First'},
                u'7': {'title': 'Third'},
                u'8': {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [u'8', u'6', u'7']}
        }))

        deserializer = getMultiAdapter(
            (self.doc, storage, self.request), IDeserializeFromJson)

        deserializer({})

        left = storage['left']
        self.assertEqual(left.blocks, {})
        self.assertEqual(left.blocks_layout, {"items": []})

    def test_delete_and_save(self):
        storage = ISlotStorage(self.doc)

        storage['left'] = Slot(**({
            'blocks': {
                u'1': {'title': 'First'},
                u'3': {'title': 'Third'},
                u'5': {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [u'5', u'1', u'3']}
        }))
        storage['right'] = Slot(**({
            'blocks': {
                u'6': {'title': 'First'},
                u'7': {'title': 'Third'},
                u'8': {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [u'8', u'6', u'7']}
        }))

        deserializer = getMultiAdapter(
            (self.doc, storage, self.request), IDeserializeFromJson)

        deserializer({
            "left": {
                'blocks_layout': {'items': [u'3', u'2', u'5', u'4']},
                'blocks': {
                    u'2': {'title': 'Second', 's:isVariantOf': u'1'},
                    u'3': {'title': 'Third', '_v_inherit': True},
                    u'5': {'title': 'Fifth', '_v_inherit': True},
                },
            },
        })

        right = storage['right']
        self.assertEqual(right.blocks, {})
        self.assertEqual(right.blocks_layout, {"items": []})

        left = storage['left']
        self.assertEqual(
            left.blocks, {u'2': {'s:isVariantOf': u'1', 'title': 'Second'}})
        self.assertEqual(left.blocks_layout, {'items': [u'2']})

    def test_delete_in_parent_affects_child(self):
        rootstorage = ISlotStorage(self.portal)
        rootstorage['left'] = Slot(**({
            'blocks': {
                u'3': {'title': 'Third'},
                u'5': {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [u'5', u'3']}
        }))

        docstorage = ISlotStorage(self.doc)

        docstorage['left'] = Slot(**({
            'blocks': {
                u'1': {'title': 'First'},
                # u'5': {'_v_inherit': True},
            },
            'blocks_layout': {'items': [u'5', u'1', u'3']}
        }))

        # self.portal.portal_catalog.indexObject(self.doc)

        deserializer = getMultiAdapter(
            (self.portal, rootstorage, self.request), IDeserializeFromJson)

        deserializer({
            "left": {
                'blocks_layout': {'items': [u'3']},
                'blocks': {
                    u'3': {'title': 'Third', },
                },
            },
        })

        self.assertEqual(rootstorage['left'].blocks,
                         {u'3': {'title': 'Third', }, })
        self.assertEqual(rootstorage['left'].blocks_layout,
                         {'items': [u'3']})

        engine = ISlots(self.doc)
        self.assertEqual(engine.get_blocks('left')['blocks_layout']['items'],
                         [u'1', u'3'])
