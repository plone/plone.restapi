# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.restapi.interfaces import ISerializeToJson
from plone.app.textfield.value import RichTextValue

from plone.restapi.testing import \
    PLONE_RESTAPI_INTEGRATION_TESTING
from DateTime import DateTime

import json


class TestSerializeToJsonAdapter(unittest.TestCase):

    layer = PLONE_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.portal.invokeFactory('Document', id='doc1', title='Document 1')

    def test_serialize_to_json_adapter_returns_hydra_context(self):
        self.assertEqual(
            json.loads(ISerializeToJson(self.portal.doc1))['@context'],
            u'http://www.w3.org/ns/hydra/context.jsonld'
        )

    def test_serialize_to_json_adapter_returns_hydra_id(self):
        self.assertEqual(
            json.loads(ISerializeToJson(self.portal.doc1))['@id'],
            self.portal_url + '/doc1'
        )

    def test_serialize_to_json_adapter_returns_hydra_type(self):
        self.assertEqual(
            json.loads(ISerializeToJson(self.portal.doc1))['@type'],
            u'Resource'
        )

    def test_serialize_to_json_adapter_returns_title(self):
        self.assertEqual(
            json.loads(ISerializeToJson(self.portal.doc1))['title'],
            u'Document 1'
        )

    def test_serialize_to_json_adapter_returns_desciption(self):
        self.portal.doc1.description = u'This is a document'
        self.assertEqual(
            json.loads(ISerializeToJson(self.portal.doc1))['description'],
            u'This is a document'
        )

    def test_serialize_to_json_adapter_returns_rich_text(self):
        self.portal.doc1.text = RichTextValue(
            u"Lorem ipsum.",
            'text/plain',
            'text/html'
        )
        self.assertEqual(
            json.loads(ISerializeToJson(self.portal.doc1)).get('text'),
            u'<p>Lorem ipsum.</p>'
        )

    def test_serialize_to_json_adapter_returns_effective(self):
        self.portal.doc1.setEffectiveDate(DateTime('2014/04/04'))
        self.assertEqual(
            json.loads(ISerializeToJson(self.portal.doc1))['effective'],
            '2014-04-04T00:00:00'
        )

    def test_serialize_to_json_adapter_returns_expires(self):
        self.portal.doc1.setExpirationDate(DateTime('2017/01/01'))
        self.assertEqual(
            json.loads(ISerializeToJson(self.portal.doc1))['expires'],
            '2017-01-01T00:00:00'
        )

    def test_serialize_to_json_adapter_on_folder_returns_member_attr(self):
        self.portal.invokeFactory('Folder', id='folder1', title='Folder 1')
        self.portal.folder1.invokeFactory('Document', id='doc1')
        self.portal.folder1.doc1.title = u'Document 1'
        self.portal.folder1.doc1.description = u'This is a document'
        self.assertEqual(
            json.loads(ISerializeToJson(self.portal.folder1))['member'],
            [
                {
                    u'@id': u'http://nohost/plone/folder1/doc1/@@json',
                    u'description': u'This is a document',
                    u'title': u'Document 1'
                }
            ]
        )

    def test_serialize_to_json_adapter_returns_portal_type(self):
        self.assertTrue(
            json.loads(ISerializeToJson(self.portal.doc1)).get('portal_type'),
            'The portal_type attribute should be present.'
        )
        self.assertEqual(
            json.loads(ISerializeToJson(self.portal.doc1))['portal_type'],
            u'Document'
        )

    def test_serialize_to_json_adapter_returns_site_root_portal_type(self):
        self.assertTrue(
            json.loads(ISerializeToJson(self.portal)).get('portal_type'),
            'The portal_type attribute should be present.'
        )
        self.assertEqual(
            json.loads(ISerializeToJson(self.portal))['portal_type'],
            u'SiteRoot'
        )

    def test_serialize_to_json_adapter_ignores_underscore_values(self):
        self.assertFalse(
            '__name__' in json.loads(ISerializeToJson(self.portal.doc1))
        )
        self.assertFalse(
            'manage_options' in json.loads(ISerializeToJson(self.portal.doc1))
        )

    def test_serialize_to_json_adapter_file(self):
        self.portal.invokeFactory('File', id='file1', title='File 1')
        self.assertEqual(
            '{0}/@@download'.format(self.portal.file1.absolute_url()),
            json.loads(ISerializeToJson(self.portal.file1)).get('download')
        )

    def test_serialize_to_json_adapter_image(self):
        self.portal.invokeFactory('Image', id='image1', title='Image 1')
        self.assertEqual(
            '{0}/@@download'.format(self.portal.image1.absolute_url()),
            json.loads(ISerializeToJson(self.portal.image1)).get('download')
        )
