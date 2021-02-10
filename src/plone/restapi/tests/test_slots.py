# -*- coding: utf-8 -*-

from plone.api import portal
from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISlots
from plone.restapi.interfaces import ISlotStorage
from plone.restapi.slots import Slot
from plone.restapi.slots import Slots
from plone.restapi.slots.interfaces import ISlotSettings
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.interface import implements
from zope.interface import Interface

import unittest


class Content(object):
    __name__ = None
    __parent__ = None

    def __init__(self, data=None):
        self.children = {}
        self.slots = {}

        self.data = data

    def __getitem__(self, key):
        return self.children[key]

    def __setitem__(self, name, child):
        child.__name__ = name
        child.__parent__ = self
        self.children[name] = child

    def __repr__(self):
        stack = []
        current = self

        while True:
            if (current.__name__):
                stack.append(current.__name__)
            if current.__parent__:
                current = current.__parent__
            else:
                break

        return "<Content: /{}>" .format("/".join(reversed(stack)))


class SlotsStorage(object):
    implements(ISlotStorage)

    def __init__(self, context):
        self.context = context

    def get(self, name):
        return self.context.slots.get(name)


class DummySlot(object):
    def __init__(self, data={}):
        self.blocks_layout = data and data['blocks_layout'] or {"items": []}
        self.blocks = data and data['blocks'] or {}

    @classmethod
    def from_data(cls, blocks, layout):
        res = {
            'blocks_layout': {"items": layout},
            'blocks': blocks
        }

        return cls(res)


class TestSlots(unittest.TestCase):
    def setUp(self):
        provideAdapter(SlotsStorage, [Interface], ISlotStorage)

    def make_content(self):

        root = Content()
        root['documents'] = Content()
        root['documents']['internal'] = Content()
        root['documents']['internal']['company-a'] = Content()
        root['documents']['internal']['company-a']['doc-1'] = Content()
        root['documents']['internal']['company-a']['doc-2'] = Content()
        root['documents']['internal']['company-a']['doc-3'] = Content()

        root['images'] = Content()

        return root

    def test_slot_stack_on_root(self):
        # simple test with one level stack of slots
        root = self.make_content()
        root.slots['left'] = DummySlot({
            'blocks': {1: {}, 2: {}, 3: {}, },
            'blocks_layout': {'items': [1, 2, 3]}
        })
        root.slots['right'] = DummySlot()
        engine = Slots(root)

        self.assertEqual(engine.get_fills_stack('bottom'), [None])

        right_stack = engine.get_fills_stack('right')
        self.assertEqual(len(right_stack), 1)
        self.assertEqual(right_stack[0].blocks_layout, {"items": []})
        self.assertEqual(right_stack[0].blocks, {})

        left_stack = engine.get_fills_stack('left')
        self.assertEqual(len(left_stack), 1)
        self.assertEqual(left_stack[0].blocks_layout, {'items': [1, 2, 3]})
        self.assertEqual(left_stack[0].blocks, {1: {}, 2: {}, 3: {}})

    def test_slot_stack_deep(self):
        # the slot stack is inherited further down
        root = self.make_content()
        root.slots['left'] = DummySlot({
            'blocks': {1: {}, 2: {}, 3: {}, },
            'blocks_layout': {'items': [1, 2, 3]}
        })
        engine = Slots(root['documents']['internal']['company-a'])

        self.assertEqual(engine.get_fills_stack('bottom'), [None, None, None, None])
        self.assertEqual(engine.get_fills_stack('right'), [None, None, None, None])

        left_stack = engine.get_fills_stack('left')
        self.assertEqual(len(left_stack), 4)

        left = left_stack[3]
        self.assertEqual(left.blocks_layout, {'items': [1, 2, 3]})
        self.assertEqual(left.blocks, {1: {}, 2: {}, 3: {}})

    def test_slot_stack_deep_with_data_in_root(self):
        # slots stacks up from deepest to shallow
        root = self.make_content()
        root.slots['left'] = DummySlot({
            'blocks': {1: {}, 2: {}, 3: {}, },
            'blocks_layout': {'items': [1, 2, 3]}
        })
        obj = root['documents']['internal']['company-a']

        slot = DummySlot.from_data({4: {}, 5: {}, 6: {}},
                                   [4, 5, 6])

        obj.slots['left'] = slot
        engine = Slots(obj)
        stack = engine.get_fills_stack('left')

        self.assertEqual(stack[1:3], [None, None])

        first = stack[0]
        self.assertEqual(first.blocks_layout, {'items': [4, 5, 6]})
        self.assertEqual(first.blocks, {4: {}, 5: {}, 6: {}})

        last = stack[3]
        self.assertEqual(last.blocks_layout, {'items': [1, 2, 3]})
        self.assertEqual(last.blocks, {1: {}, 2: {}, 3: {}})

    def test_slot_stack_deep_with_stack_collapse(self):
        # get_blocks collapses the stack and marks inherited slots with _v_inherit

        root = self.make_content()
        obj = root['documents']['internal']['company-a']

        root.slots['left'] = DummySlot.from_data({1: {}, 2: {}, 3: {}, }, [1, 2, 3])

        root['documents'].slots['left'] = DummySlot.from_data({4: {}, 5: {}, 6: {}},
                                                              [4, 5, 6])

        obj.slots['left'] = DummySlot.from_data({4: {}, 5: {}, 6: {}, 7: {}},
                                                [4, 5, 6, 7])

        engine = Slots(obj)

        left = engine.get_blocks('left')
        self.assertEqual(left, {
            'blocks_layout': {'items': [4, 5, 6, 7, 1, 2, 3]},
            'blocks': {
                4: {},
                5: {},
                6: {},
                1: {'_v_inherit': True, },
                2: {'_v_inherit': True, },
                3: {'_v_inherit': True, },
                7: {}
            }
        })

    def test_block_data_gets_inherited(self):
        # blocks that are inherited from parents are marked with _v_inherit

        root = self.make_content()
        obj = root['documents']['internal']

        root['documents'].slots['left'] = DummySlot.from_data(
            {1: {'title': 'First'}}, [1])
        obj.slots['left'] = DummySlot.from_data({2: {}}, [2])

        engine = Slots(obj)
        left = engine.get_blocks('left')

        self.assertEqual(left, {
            'blocks_layout': {'items': [2, 1]},
            'blocks': {
                1: {'title': 'First', '_v_inherit': True},
                2: {}
            }
        })

    def test_block_data_gets_override(self):
        # a child can override the data for a parent block, in a new block

        root = self.make_content()

        root['documents'].slots['left'] = DummySlot.from_data({
            1: {'title': 'First'},
            3: {'title': 'Third'},
        }, [1, 3])

        obj = root['documents']['internal']
        obj.slots['left'] = DummySlot.from_data({
            2: {'s:isVariantOf': 1, 'title': 'Second'}},
            [2])

        engine = Slots(obj)
        left = engine.get_blocks('left')

        self.assertEqual(left, {
            'blocks_layout': {'items': [2, 3]},
            'blocks': {
                2: {'title': 'Second', 's:isVariantOf': 1},
                3: {'title': 'Third', '_v_inherit': True},
            }
        })

    def test_can_change_order_with_sameOf(self):
        # a child can change the order inherited from its parents
        # to reposition a parent,

        root = self.make_content()

        root['documents'].slots['left'] = DummySlot.from_data({
            1: {'title': 'First'},
            3: {'title': 'Third'},
            5: {'title': 'Fifth'},
        }, [5, 1, 3])

        obj = root['documents']['internal']
        obj.slots['left'] = DummySlot.from_data({
            2: {'s:isVariantOf': 1, 'title': 'Second'},
            4: {'s:sameAs': 3}
        }, [4, 2])

        engine = Slots(obj)
        left = engine.get_blocks('left')

        self.assertEqual(left, {
            'blocks_layout': {'items': [4, 2, 5]},
            'blocks': {
                2: {'title': 'Second', 's:isVariantOf': 1},
                4: {'title': 'Third', 's:sameAs': 3, '_v_inherit': True},
                5: {'title': 'Fifth', '_v_inherit': True},
            }
        })

    def test_can_change_order_from_layout(self):
        # a child can change the order inherited from parents by simply repositioning
        # the parent id in their layout

        root = self.make_content()

        root['documents'].slots['left'] = DummySlot.from_data({
            1: {'title': 'First'},
            3: {'title': 'Third'},
            5: {'title': 'Fifth'},
        }, [5, 1, 3])

        obj = root['documents']['internal']
        obj.slots['left'] = DummySlot.from_data({
            2: {'s:isVariantOf': 1, 'title': 'Second'},
        }, [3, 2])

        engine = Slots(obj)
        left = engine.get_blocks('left')

        self.assertEqual(left, {
            'blocks_layout': {'items': [3, 2, 5]},
            'blocks': {
                2: {'title': 'Second', 's:isVariantOf': 1},
                3: {'title': 'Third', '_v_inherit': True},
                5: {'title': 'Fifth', '_v_inherit': True},
            }
        })

    def test_save_slots(self):
        data = {
            'blocks_layout': {'items': [3, 2, 5]},
            'blocks': {
                2: {'title': 'Second', 's:isVariantOf': 1},
                3: {'title': 'Third', '_v_inherit': True},
                5: {'title': 'Fifth', '_v_inherit': True},
            },
        }

        root = self.make_content()
        obj = root['documents']['internal']
        engine = Slots(obj)

        slot = DummySlot()
        engine.save_data_to_slot(slot, data)

        self.assertEqual(slot.blocks, {2: {'s:isVariantOf': 1, 'title': 'Second'}})
        self.assertEqual(slot.blocks_layout, {'items': [3, 2, 5]})


class TestSlotsStorage(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

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

    def test_serialize_slots_storage_portal(self):
        storage = ISlotStorage(self.portal)

        self.assertEqual(storage.__name__, 'plone.restapi.slots')

    def test_serialize_slots_storage(self):
        storage = ISlotStorage(self.doc)

        self.assertEqual(storage.__name__, 'plone.restapi.slots')
        self.assertTrue(storage.__parent__ is self.doc)
        self.assertTrue(storage.__parent__ is self.doc)

    def test_store_slots_in_storage(self):
        storage = ISlotStorage(self.doc)
        storage['left'] = Slot()

        self.assertEqual(storage['left'].__name__, 'left')
        self.assertTrue(storage['left'].__parent__ is storage)


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

    def test_editable_slots_as_manager(self):
        engine = ISlots(self.doc)

        empty = engine.get_editable_slots()
        self.assertEqual(empty, [])

        storage = ISlotStorage(self.doc)
        storage['left'] = Slot()

        left = engine.get_editable_slots()
        self.assertEqual(left, ['left'])

    def test_editable_slots_as_member(self):
        self.login('simple_member')

        engine = ISlots(self.doc)

        empty = engine.get_editable_slots()
        self.assertEqual(empty, [])

        storage = ISlotStorage(self.doc)
        storage['left'] = Slot()

        left = engine.get_editable_slots()
        self.assertEqual(left, [])

        registry = portal.get_tool('portal_registry')
        proxy = registry.forInterface(ISlotSettings)
        proxy.content_slots = [u'left']

        self.assertEqual(engine.get_editable_slots(), [])

    def test_editable_slots_as_editor(self):
        self.login('editor_member')

        engine = ISlots(self.doc)

        empty = engine.get_editable_slots()
        self.assertEqual(empty, [])

        storage = ISlotStorage(self.doc)
        storage['left'] = Slot()

        left = engine.get_editable_slots()
        self.assertEqual(left, [])

        registry = portal.get_tool('portal_registry')
        proxy = registry.forInterface(ISlotSettings)
        proxy.content_slots = [u'left']

        self.assertEqual(engine.get_editable_slots(), [u'left'])

    def test_deserialize_empty(self):
        storage = ISlotStorage(self.doc)
        deserializer = getMultiAdapter(
            (self.doc, storage,  self.request), IDeserializeFromJson)
        deserializer()

        self.assertEqual(list(storage.keys()), [])

    def test_deserialize_put_one(self):
        storage = ISlotStorage(self.doc)
        deserializer = getMultiAdapter(
            (self.doc, storage,  self.request), IDeserializeFromJson)
        deserializer({"left": {
            'blocks_layout': {'items': [3, 2, 5]},
            'blocks': {
                2: {'title': 'Second', 's:isVariantOf': 1},
                3: {'title': 'Third', '_v_inherit': True},
                5: {'title': 'Fifth', '_v_inherit': True},
            }
        }})

        self.assertEqual(list(storage.keys()), ['left'])
