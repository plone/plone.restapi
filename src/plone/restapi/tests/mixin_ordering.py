# -*- coding: utf-8 -*-
import json

from zExceptions import BadRequest


class OrderingMixin():
    # This assumes there is a self.folder with 9 documents in it.

    def test_reorder(self):
        # We run all this in one test, because of dependend ordering.
        # initial situation
        self.assertEquals(
            ['doc1', 'doc2', 'doc3', 'doc4', 'doc5', 'doc6', 'doc7', 'doc8', 'doc9', ],  # noqa
            self.folder.contentIds()
        )

        # Normal
        # Move to top
        data = {'ordering': {'delta': 'top', 'obj_id': 'doc9'}}
        self.deserialize(body=json.dumps(data), context=self.folder)
        self.assertEquals(
            ['doc9', 'doc1', 'doc2', 'doc3', 'doc4', 'doc5', 'doc6', 'doc7', 'doc8', ],  # noqa
            self.folder.contentIds()
        )

        # Move to bottom
        data = {'ordering': {'delta': 'bottom', 'obj_id': 'doc9'}}
        self.deserialize(body=json.dumps(data), context=self.folder)
        self.assertEquals(
            ['doc1', 'doc2', 'doc3', 'doc4', 'doc5', 'doc6', 'doc7', 'doc8', 'doc9', ],  # noqa
            self.folder.contentIds()
        )

        # Delta up
        data = {'ordering': {'delta': -2, 'obj_id': 'doc5'}}
        self.deserialize(body=json.dumps(data), context=self.folder)
        self.assertEquals(
            ['doc1', 'doc2', 'doc5', 'doc3', 'doc4', 'doc6', 'doc7', 'doc8', 'doc9', ],  # noqa
            self.folder.contentIds()
        )

        # Delta down
        data = {'ordering': {'delta': 2, 'obj_id': 'doc6'}}
        self.deserialize(body=json.dumps(data), context=self.folder)
        self.assertEquals(
            ['doc1', 'doc2', 'doc5', 'doc3', 'doc4', 'doc7', 'doc8', 'doc6', 'doc9', ],  # noqa
            self.folder.contentIds()
        )

        # subset ids
        # Move to top
        data = {'ordering': {'delta': 'top', 'obj_id': 'doc8', 'subset_ids': ['doc2', 'doc3', 'doc8']}}  # noqa
        self.deserialize(body=json.dumps(data), context=self.folder)
        self.assertEquals(
            ['doc1', 'doc8', 'doc5', 'doc2', 'doc4', 'doc7', 'doc3', 'doc6', 'doc9'],  # noqa
            self.folder.contentIds()
        )

        # Move to bottom
        data = {'ordering': {'delta': 'bottom', 'obj_id': 'doc8', 'subset_ids': ['doc8', 'doc2', 'doc3']}}  # noqa
        self.deserialize(body=json.dumps(data), context=self.folder)
        self.assertEquals(
            ['doc1', 'doc2', 'doc5', 'doc3', 'doc4', 'doc7', 'doc8', 'doc6', 'doc9'],  # noqa
            self.folder.contentIds()
        )

        # Delta up
        data = {'ordering': {'delta': -1, 'obj_id': 'doc8', 'subset_ids': ['doc2', 'doc3', 'doc8']}}  # noqa
        self.deserialize(body=json.dumps(data), context=self.folder)
        self.assertEquals(
            ['doc1', 'doc2', 'doc5', 'doc8', 'doc4', 'doc7', 'doc3', 'doc6', 'doc9'],  # noqa
            self.folder.contentIds()
        )

        # Delta down
        data = {'ordering': {'delta': 1, 'obj_id': 'doc2', 'subset_ids': ['doc2', 'doc8', 'doc3']}}  # noqa
        self.deserialize(body=json.dumps(data), context=self.folder)
        self.assertEquals(
            ['doc1', 'doc8', 'doc5', 'doc2', 'doc4', 'doc7', 'doc3', 'doc6', 'doc9'],  # noqa
            self.folder.contentIds()
        )

    def test_reorder_subsetids(self):
        # sanity check, initial situation
        self.assertEquals(
            ['doc1', 'doc2', 'doc3', 'doc4', 'doc5', 'doc6', 'doc7', 'doc8', 'doc9'],  # noqa
            self.folder.contentIds()
        )

        data = {'ordering': {'delta': 1, 'obj_id': 'doc8', 'subset_ids': ['doc2', 'doc8', 'doc6']}}  # noqa

        with self.assertRaises(BadRequest) as cm:
            self.deserialize(body=json.dumps(data), context=self.folder)

        self.assertEquals(
            u'Client/server ordering mismatch',
            cm.exception.message
        )
