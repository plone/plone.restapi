# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.utils import append_json_to_links
from plone.restapi.utils import get_object_schema
from plone.restapi.testing import PLONE_RESTAPI_INTEGRATION_TESTING

import unittest

try:
    from Products.CMFPlone.factory import _IMREALLYPLONE5  # noqa
except ImportError:
    ADDITIONAL_PLONE_5_FIELDS = []  # pragma: no cover
else:
    ADDITIONAL_PLONE_5_FIELDS = ['id']  # pragma: no cover

BASE_SCHEMA = [
    'title',
    'allow_discussion',
    'exclude_from_nav',
    'relatedItems',
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
] + ADDITIONAL_PLONE_5_FIELDS


class GetObjectSchemaUnitTest(unittest.TestCase):

    layer = PLONE_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_get_object_schema_for_document(self):
        self.portal.invokeFactory('Document', id='doc1', title='Doc 1')
        schema = [x[0] for x in get_object_schema(self.portal.doc1)]
        self.assertEqual(
            set(schema),
            set(BASE_SCHEMA + [
                'table_of_contents',
                'text',
                'changeNote',
            ])
        )

    def test_get_object_schema_for_folder(self):
        self.portal.invokeFactory('Folder', id='folder1', title='Folder 1')
        schema = [x[0] for x in get_object_schema(self.portal.folder1)]
        self.assertEqual(
            set(schema),
            set(BASE_SCHEMA + [
                'nextPreviousEnabled',
                'isAnObjectManager',
                'meta_types'
            ])
        )

    def test_get_object_schema_for_news_item(self):
        self.portal.invokeFactory(
            'News Item',
            id='newsitem1',
            title='News Item 1'
        )
        schema = [x[0] for x in get_object_schema(self.portal.newsitem1)]
        self.assertEqual(
            set(schema),
            set(BASE_SCHEMA + [
                # 'table_of_contents', XXX: Why no toc?
                'text',
                'changeNote',
                'image',
                'image_caption',
            ])
        )

    def test_get_object_schema_for_image(self):
        self.portal.invokeFactory(
            'Image',
            id='image1',
            title='Image 1'
        )
        schema = [x[0] for x in get_object_schema(self.portal.image1)]
        self.assertEqual(
            set(schema),
            set(BASE_SCHEMA + ['image'])
        )


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
