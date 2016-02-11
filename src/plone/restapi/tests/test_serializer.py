# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.restapi.interfaces import ISerializeToJson
from plone.app.textfield.value import RichTextValue
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from plone.namedfile.file import NamedBlobImage
from DateTime import DateTime
from zope.component import getMultiAdapter

import os
import unittest


class TestSerializeToJsonAdapter(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.workflowTool = getToolByName(self.portal, 'portal_workflow')
        self.portal_url = self.portal.absolute_url()
        self.portal.invokeFactory('Document', id='doc1', title='Document 1')
        self.portal.invokeFactory(
            'DXTestDocument',
            id='dxdoc',
            title='DX Test Document'
        )

    def serialize(self, obj):
        serializer = getMultiAdapter((obj, self.request),
                                     ISerializeToJson)
        return serializer()

    def test_serialize_returns_context(self):
        self.assertEqual(
            self.serialize(self.portal.doc1)['@context'],
            u'http://www.w3.org/ns/hydra/context.jsonld'
        )

    def test_serialize_returns_id(self):
        self.assertEqual(
            self.serialize(self.portal.doc1)['@id'],
            self.portal_url + '/doc1'
        )

    def test_serialize_returns_type(self):
        self.assertTrue(
            self.serialize(self.portal.doc1).get('@type'),
            'The @type attribute should be present.'
        )
        self.assertEqual(
            self.serialize(self.portal.doc1)['@type'],
            u'Document'
        )

    def test_serialize_returns_title(self):
        self.assertEqual(
            self.serialize(self.portal.doc1)['title'],
            u'Document 1'
        )

    def test_serialize_can_read_as_manager(self):
        self.portal.dxdoc.test_read_permission_field = u'Test Read Permission'
        self.workflowTool.doActionFor(self.portal.dxdoc, 'publish')
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])
        self.assertIn(
            'Test Read Permission',
            self.serialize(self.portal.dxdoc).values()
        )

    def test_serialize_cannot_read_as_member(self):
        self.portal.dxdoc.test_read_permission_field = u'Test Read Permission'
        self.workflowTool.doActionFor(self.portal.dxdoc, 'publish')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertNotIn(
            'Test Read Permission',
            self.serialize(self.portal.dxdoc).values()
        )

    def test_serialize_returns_desciption(self):
        self.portal.doc1.description = u'This is a document'
        self.assertEqual(
            self.serialize(self.portal.doc1)['description'],
            u'This is a document'
        )

    def test_serialize_returns_rich_text(self):
        self.portal.doc1.text = RichTextValue(
            u"Lorem ipsum.",
            'text/plain',
            'text/html'
        )
        self.assertEqual(
            self.serialize(self.portal.doc1).get('text'),
            u'<p>Lorem ipsum.</p>'
        )

    def test_serialize_returns_effective(self):
        self.portal.doc1.setEffectiveDate(DateTime('2014/04/04'))
        self.assertEqual(
            self.serialize(self.portal.doc1)['effective'],
            '2014-04-04T00:00:00'
        )

    def test_serialize_returns_expires(self):
        self.portal.doc1.setExpirationDate(DateTime('2017/01/01'))
        self.assertEqual(
            self.serialize(self.portal.doc1)['expires'],
            '2017-01-01T00:00:00'
        )

    def test_serialize_on_folder_returns_member_attr(self):
        self.portal.invokeFactory('Folder', id='folder1', title='Folder 1')
        self.portal.folder1.invokeFactory('Document', id='doc1')
        self.portal.folder1.doc1.title = u'Document 1'
        self.portal.folder1.doc1.description = u'This is a document'
        self.assertEqual(
            self.serialize(self.portal.folder1)['member'],
            [
                {
                    u'@id': u'http://nohost/plone/folder1/doc1',
                    u'description': u'This is a document',
                    u'title': u'Document 1'
                }
            ]
        )

    def test_serialize_returns_parent(self):
        self.assertTrue(
            self.serialize(self.portal.doc1).get('parent'),
            'The parent attribute should be present.'
        )
        self.assertEqual(
            {
                '@id': self.portal.absolute_url(),
                'title': self.portal.title,
                'description': self.portal.description
            },
            self.serialize(self.portal.doc1)['parent']
        )

    def test_serialize_does_not_returns_parent_on_root(self):
        self.assertEqual(
            {},
            self.serialize(self.portal).get('parent'),
            'The parent attribute should be present, even on portal root.'
        )
        self.assertEqual(
            {
                '@id': self.portal.absolute_url(),
                'title': self.portal.title,
                'description': self.portal.description
            },
            self.serialize(self.portal.doc1)['parent'],
            'The parent attribute on portal root should be None'
        )

    def test_serialize_returns_site_root_type(self):
        self.assertTrue(
            self.serialize(self.portal).get('@type'),
            'The @type attribute should be present.'
        )
        self.assertEqual(
            self.serialize(self.portal)['@type'],
            u'Plone Site'
        )

    def test_serialize_ignores_underscore_values(self):
        self.assertFalse(
            '__name__' in self.serialize(self.portal.doc1)
        )
        self.assertFalse(
            'manage_options' in self.serialize(self.portal.doc1)
        )

    def test_serialize_file(self):
        self.portal.invokeFactory('File', id='file1', title='File 1')
        self.assertEqual(
            '{0}/@@download/file'.format(self.portal.file1.absolute_url()),
            self.serialize(self.portal.file1).get('file')
        )

    def test_serialize_image(self):
        self.portal.invokeFactory('Image', id='image1', title='Image 1')
        image_file = os.path.join(os.path.dirname(__file__), u'image.png')
        self.portal.image1.image = NamedBlobImage(
            data=open(image_file, 'r').read(),
            contentType='image/png',
            filename=u'image.png'
        )

        obj_url = self.portal.image1.absolute_url()
        self.assertDictEqual(
            {u'original': u'{}/@@images/image'.format(obj_url),
             u'mini': u'{}/@@images/image/mini'.format(obj_url),
             u'thumb': u'{}/@@images/image/thumb'.format(obj_url),
             u'large': u'{}/@@images/image/large'.format(obj_url),
             u'listing': u'{}/@@images/image/listing'.format(obj_url),
             u'tile': u'{}/@@images/image/tile'.format(obj_url),
             u'preview': u'{}/@@images/image/preview'.format(obj_url),
             u'icon': u'{}/@@images/image/icon'.format(obj_url)},
            self.serialize(self.portal.image1)['image'])

    def test_serialize_to_json_collection(self):
        self.portal.invokeFactory('Collection', id='collection1')
        self.portal.collection1.title = 'My Collection'
        self.portal.collection1.description = \
            u'This is a collection with two documents'
        self.portal.collection1.query = [{
            'i': 'portal_type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Document',
        }]
        self.portal.invokeFactory(
            'Document',
            id='doc2',
            title='Document 2'
        )
        self.portal.doc1.reindexObject()
        self.portal.doc2.reindexObject()

        self.assertEqual(
            u'Collection',
            self.serialize(self.portal.collection1).get('@type')
        )
        self.assertEqual(
            u'Collection',
            self.serialize(self.portal.collection1).get('@type')
        )
        self.assertEqual(
            [
                {
                    u'@id': self.portal.doc1.absolute_url(),
                    u'description': u'',
                    u'title': u'Document 1'
                },
                {
                    u'@id': self.portal.doc2.absolute_url(),
                    u'description': u'',
                    u'title': u'Document 2'
                }
            ],
            self.serialize(self.portal.collection1).get('member')
        )
