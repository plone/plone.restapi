# -*- coding: utf-8 -*-

from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.slots import Slot
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
                'blocks_layout': {'items': [3, 2, 5, 4]},
                'blocks': {
                    2: {'title': 'Second', 's:isVariantOf': 1},
                    3: {'title': 'Third', '_v_inherit': True},
                    5: {'title': 'Fifth', '_v_inherit': True},
                },
            },
            "right": {
                'blocks_layout': {'items': [6, 7]},
                'blocks': {
                    6: {'title': 'Sixth'},
                }
            }
        })

        self.assertEqual(list(storage.keys()), ['left', 'right'])
        self.assertEqual(storage['left'].blocks,
                         {2: {'title': 'Second', 's:isVariantOf': 1}, })
        self.assertEqual(storage['left'].blocks_layout, {"items": [3, 2, 5, 4]})

        self.assertEqual(storage['right'].blocks,
                         {6: {'title': 'Sixth'}, })
        self.assertEqual(storage['right'].blocks_layout, {"items": [6, 7]})

    def test_delete_all_with_dict(self):
        storage = ISlotStorage(self.doc)

        storage['left'] = Slot(**({
            'blocks': {
                1: {'title': 'First'},
                3: {'title': 'Third'},
                5: {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [5, 1, 3]}
        }))
        storage['right'] = Slot(**({
            'blocks': {
                6: {'title': 'First'},
                7: {'title': 'Third'},
                8: {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [8, 6, 7]}
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
                1: {'title': 'First'},
                3: {'title': 'Third'},
                5: {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [5, 1, 3]}
        }))
        storage['right'] = Slot(**({
            'blocks': {
                6: {'title': 'First'},
                7: {'title': 'Third'},
                8: {'title': 'Fifth'},
            },
            'blocks_layout': {'items': [8, 6, 7]}
        }))

        deserializer = getMultiAdapter(
            (self.doc, storage, self.request), IDeserializeFromJson)

        deserializer({})

        left = storage['left']
        self.assertEqual(left.blocks, {})
        self.assertEqual(left.blocks_layout, {"items": []})
