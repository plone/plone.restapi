# -*- coding: utf-8 -*-
import unittest2 as unittest
from plone.restapi.utils import append_json_to_links
from plone.restapi.utils import get_object_schema
from plone.restapi.utils import underscore_to_camelcase
from plone.restapi.testing import\
    PLONE_RESTAPI_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class GetObjectSchemaUnitTest(unittest.TestCase):

    layer = PLONE_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_get_object_schema_for_document(self):
        self.portal.invokeFactory('Document', id='doc1', title='Doc 1')
        schema = [x[0] for x in get_object_schema(self.portal.doc1)]
        expected_fields = [
            'text',
            'title',
            'allow_discussion',
            'exclude_from_nav',
            'relatedItems',
            'table_of_contents',
            'meta_type',
            'isPrincipiaFolderish',
            'icon',
            'rights',
            'contributors',
            'effective',
            'expires',
            'language',
            'subjects',
            'creators',
            'description',
            'changeNote'
        ]
        for expected_field in expected_fields:
            self.assertTrue(
                expected_field in schema,
            )

    def test_get_object_schema_for_folder(self):
        self.portal.invokeFactory('Folder', id='folder1', title='Folder 1')
        schema = [x[0] for x in get_object_schema(self.portal.folder1)]
        expected_fields = [
            'title',
            'allow_discussion',
            'exclude_from_nav',
            'relatedItems',
            'nextPreviousEnabled',
            'isAnObjectManager',
            'meta_type',
            'meta_types',
            'isPrincipiaFolderish',
            'icon',
            'rights',
            'contributors',
            'effective',
            'expires',
            'language',
            'subjects',
            'creators',
            'description'
        ]
        for expected_field in expected_fields:
            self.assertTrue(
                expected_field in schema,
            )


class UnderscoreToCamelcaseUnitTest(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(underscore_to_camelcase(''), '')

    def test_simple_term(self):
        self.assertEqual(underscore_to_camelcase('lorem'), 'Lorem')

    def test_two_simple_terms(self):
        self.assertEqual(underscore_to_camelcase('lorem_ipsum'), 'LoremIpsum')


class AppendJsonToLinksUnitTest(unittest.TestCase):

    def test_empty(self):
        self.assertEqual({}, append_json_to_links({}))

    def test_append_json_to_id(self):
        self.assertEqual(
            {'@id': 'http://foo.com/@@json'},
            append_json_to_links({'@id': 'http://foo.com'})
        )

    def test_append_json_to_member_ids(self):
        self.assertEqual(
            {'member': [{'@id': 'http://foo.com/@@json'}]},
            append_json_to_links({'member': [{'@id': 'http://foo.com'}]})
        )

    def test_append_json_to_parent_ids(self):
        self.assertEqual(
            {'parent': {'@id': 'http://foo.com/@@json'}},
            append_json_to_links({'parent': {'@id': 'http://foo.com'}})
        )
