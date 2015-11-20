# -*- coding: utf-8 -*-
from plone.restapi.utils import append_json_to_links
import unittest


class AppendJsonToLinksUnitTest(unittest.TestCase):

    def test_empty(self):
        self.assertEqual({}, append_json_to_links({}))

    def test_append_json_to_id(self):
        self.assertEqual(
            {'@id': 'http://foo.com?format=json'},
            append_json_to_links({'@id': 'http://foo.com'})
        )

    def test_append_json_to_member_ids(self):
        self.assertEqual(
            {'member': [{'@id': 'http://foo.com?format=json'}]},
            append_json_to_links({'member': [{'@id': 'http://foo.com'}]})
        )

    def test_append_json_to_parent_ids(self):
        self.assertEqual(
            {'parent': {'@id': 'http://foo.com?format=json'}},
            append_json_to_links({'parent': {'@id': 'http://foo.com'}})
        )
