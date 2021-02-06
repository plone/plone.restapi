# -*- coding: utf-8 -*-

from copy import deepcopy
from six.moves import UserDict

import unittest


_missing = object()


class SlotsEngine(object):
    def __init__(self, context):
        self.context = context

    def get_slots_stack(self, name):
        slot_stack = []

        current = self.context
        while True:
            slot = current.slots.get(name)
            if slot:
                slot_stack.append(slot)
            if current.__parent__:
                current = current.__parent__
            else:
                break

        return slot_stack

    def get_slots(self, name):
        blocks = {}
        blocks_layout = []

        _override = set()

        stack = self.get_slots_stack(name)

        level = 0
        for slot in stack:
            for uid, block in slot['slot_blocks'].items():
                block = deepcopy(block)

                if not (uid in blocks or uid in _override):
                    if block.get('_override'):
                        _override.add(block['_override'])

                    blocks[uid] = block
                    if level > 0:
                        block['_v_inherit'] = True

            for uid in slot['slot_blocks_layout']['items']:
                if uid not in blocks_layout and uid not in _override:
                    blocks_layout.append(uid)

            level += 1

        return {
            'slot_blocks': blocks,
            'slot_blocks_layout': {'items': blocks_layout}
        }


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


class Slot(UserDict):

    @classmethod
    def from_data(cls, blocks, layout):
        res = {
            'slot_blocks_layout': {"items": layout},
            'slot_blocks': blocks
        }

        return cls(res)


class TestSlots(unittest.TestCase):

    def make_content(self):

        root = Content()
        root['documents'] = Content()
        root['documents']['internal'] = Content()
        root['documents']['internal']['company-a'] = Content()
        root['documents']['internal']['company-a']['doc-1'] = Content()
        root['documents']['internal']['company-a']['doc-2'] = Content()
        root['documents']['internal']['company-a']['doc-3'] = Content()

        root['documents']['external'] = Content()
        root['documents']['external']['company-a'] = Content()
        root['documents']['external']['company-a']['doc-1'] = Content()
        root['documents']['external']['company-a']['doc-2'] = Content()
        root['documents']['external']['company-a']['doc-3'] = Content()

        root['images'] = Content()

        return root

    def test_slot_stack_on_root(self):
        # simple test with one level stack of slots
        root = self.make_content()
        root.slots['left'] = Slot({
            'slot_blocks': {1: {}, 2: {}, 3: {}, },
            'slot_blocks_layout': {'items': [1, 2, 3]}
        })
        root.slots['right'] = Slot()
        engine = SlotsEngine(root)

        self.assertEqual(engine.get_slots_stack('bottom'), [])
        self.assertEqual(engine.get_slots_stack('right'), [])
        self.assertEqual(engine.get_slots_stack('left'), [
            {
                'slot_blocks_layout': {'items': [1, 2, 3]},
                'slot_blocks': {1: {}, 2: {}, 3: {}}
            }
        ])

    def test_slot_stack_deep(self):
        # the slot stack is inherited further down
        root = self.make_content()
        root.slots['left'] = Slot({
            'slot_blocks': {1: {}, 2: {}, 3: {}, },
            'slot_blocks_layout': {'items': [1, 2, 3]}
        })
        engine = SlotsEngine(root['documents']['internal']['company-a'])

        self.assertEqual(engine.get_slots_stack('bottom'), [])
        self.assertEqual(engine.get_slots_stack('right'), [])
        self.assertEqual(engine.get_slots_stack('left'), [
            {'slot_blocks_layout': {'items': [1, 2, 3]},
             'slot_blocks': {1: {}, 2: {}, 3: {}}}
        ])

    def test_slot_stack_deep_with_data_in_root(self):
        # slots stacks up from deepest to shallow
        root = self.make_content()
        root.slots['left'] = Slot({
            'slot_blocks': {1: {}, 2: {}, 3: {}, },
            'slot_blocks_layout': {'items': [1, 2, 3]}
        })
        obj = root['documents']['internal']['company-a']

        slot = Slot.from_data({4: {}, 5: {}, 6: {}},
                              [4, 5, 6])

        obj.slots['left'] = slot
        engine = SlotsEngine(obj)

        self.assertEqual(engine.get_slots_stack('left'), [
            {
                'slot_blocks_layout': {'items': [4, 5, 6]},
                'slot_blocks': {4: {}, 5: {}, 6: {}}},
            {
                'slot_blocks_layout': {'items': [1, 2, 3]},
                'slot_blocks': {1: {}, 2: {}, 3: {}}}
        ])

    def test_slot_stack_deep_with_stack_collapse(self):
        # get_slots collapses the stack and marks inherited slots with _v_inherit

        root = self.make_content()
        obj = root['documents']['internal']['company-a']

        root.slots['left'] = Slot.from_data({1: {}, 2: {}, 3: {}, }, [1, 2, 3])

        root['documents'].slots['left'] = Slot.from_data({4: {}, 5: {}, 6: {}},
                                                         [4, 5, 6])

        obj.slots['left'] = Slot.from_data({4: {}, 5: {}, 6: {}, 7: {}},
                                           [4, 5, 6, 7])

        engine = SlotsEngine(obj)

        left = engine.get_slots('left')
        self.assertEqual(left, {
            'slot_blocks_layout': {'items': [4, 5, 6, 7, 1, 2, 3]},
            'slot_blocks': {
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

        root['documents'].slots['left'] = Slot.from_data({1: {'title': 'First'}}, [1])
        obj.slots['left'] = Slot.from_data({2: {}}, [2])

        engine = SlotsEngine(obj)
        left = engine.get_slots('left')

        self.assertEqual(left, {
            'slot_blocks_layout': {'items': [2, 1]},
            'slot_blocks': {
                1: {'title': 'First', '_v_inherit': True},
                2: {}
            }
        })

    def test_block_data_gets_override(self):
        root = self.make_content()

        root['documents'].slots['left'] = Slot.from_data({
            1: {'title': 'First'},
            3: {'title': 'Third'},
        }, [1, 3])

        obj = root['documents']['internal']
        obj.slots['left'] = Slot.from_data({
            2: {'_override': 1, 'title': 'Second'}},
            [2])

        engine = SlotsEngine(obj)
        left = engine.get_slots('left')

        self.assertEqual(left, {
            'slot_blocks_layout': {'items': [2, 3]},
            'slot_blocks': {
                2: {'title': 'Second', '_override': 1},
                3: {'title': 'Third', '_v_inherit': True},
            }
        })

    # def test_block_data_gets_override_complex(self):
    #     root = self.make_content()
    #
    #     root.slots['left'] = Slot.from_data({
    #         1: {'title': 'First'},
    #         3: {'title': 'Third'},
    #     }, [1, 3])
    #
    #     root['documents'].slots['left'] = Slot.from_data({
    #         2: {'title': 'Second'},
    #         4: {'_override': 3},
    #     }, [2, 4])
    #
    #     obj = root['documents']['internal']
    #     obj.slots['left'] = Slot.from_data({
    #         2: {'_override': 1, 'title': 'Second'}},
    #         [2])
    #
    #     engine = SlotsEngine(obj)
    #     left = engine.get_slots('left')
    #
    #     self.assertEqual(left, {
    #         'slot_blocks_layout': {'items': [2, 3]},
    #         'slot_blocks': {
    #             2: {'title': 'Second', '_override': 1},
    #             3: {'title': 'Third', '_v_inherit': True},
    #         }
    #     })
