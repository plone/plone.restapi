# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from mock import patch
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import iterSchemata
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.testing import PLONE_VERSION
from plone.scale import storage
from unittest import TestCase
from z3c.form.interfaces import IDataManager
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass

import os
import six

if PLONE_VERSION.base_version >= '5.1':
    GIF_SCALE_FORMAT = 'png'
else:
    GIF_SCALE_FORMAT = 'jpeg'


class TestDexterityFieldSerializing(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING
    maxDiff = None

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.doc1 = self.portal[self.portal.invokeFactory(
            'DXTestDocument',
            id='doc1',
            title='Test Document'
        )]

    def serialize(self, fieldname, value):
        for schema in iterSchemata(self.doc1):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        dm = getMultiAdapter(
            (self.doc1, field),
            IDataManager
        )
        dm.set(value)
        serializer = getMultiAdapter(
            (field, self.doc1, self.request),
            IFieldSerializer
        )
        return serializer()

    def test_ascii_field_serialization_returns_unicode(self):
        value = self.serialize('test_ascii_field', 'foo')
        self.assertTrue(isinstance(value, six.text_type), 'Not an <unicode>')
        self.assertEqual(u'foo', value)

    def test_asciiline_field_serialization_returns_unicode(self):
        value = self.serialize('test_asciiline_field', 'foo')
        self.assertTrue(isinstance(value, six.text_type), 'Not an <unicode>')
        self.assertEqual(u'foo', value)

    def test_bool_field_serialization_returns_true(self):
        value = self.serialize('test_bool_field', True)
        self.assertTrue(isinstance(value, bool), 'Not a <bool>')
        self.assertEqual(True, value)

    def test_bool_field_serialization_returns_false(self):
        value = self.serialize('test_bool_field', False)
        self.assertTrue(isinstance(value, bool), 'Not a <bool>')
        self.assertEqual(False, value)

    def test_bytes_field_serialization_returns_unicode(self):
        value = self.serialize('test_bytes_field', b'\xc3\xa4\xc3\xb6\xc3\xbc')
        self.assertTrue(isinstance(value, six.text_type), 'Not an <unicode>')
        self.assertEqual(u'\xe4\xf6\xfc', value)

    def test_bytesline_field_serialization_returns_unicode(self):
        value = self.serialize('test_bytesline_field',
                               b'\xc3\xa4\xc3\xb6\xc3\xbc')
        self.assertTrue(isinstance(value, six.text_type), 'Not an <unicode>')
        self.assertEqual(u'\xe4\xf6\xfc', value)

    def test_choice_field_serialization_returns_vocabulary_item(self):
        value = self.serialize('test_choice_field', u'foo')
        self.assertTrue(isinstance(value, six.text_type), 'Not an <unicode>')
        self.assertEqual(u'foo', value)

    def test_date_field_serialization_returns_unicode(self):
        value = self.serialize('test_date_field', date(2015, 7, 15))
        self.assertTrue(isinstance(value, six.text_type), 'Not an <unicode>')
        self.assertEqual(u'2015-07-15', value)

    def test_datetime_field_serialization_returns_unicode(self):
        value = self.serialize('test_datetime_field',
                               datetime(2015, 6, 20, 13, 22, 4))
        self.assertTrue(isinstance(value, six.text_type), 'Not an <unicode>')
        self.assertEqual(u'2015-06-20T13:22:04', value)

    def test_decimal_field_serialization_returns_unicode(self):
        value = self.serialize('test_decimal_field', '1.1')
        self.assertTrue(isinstance(value, six.text_type), 'Not an <unicode>')
        self.assertEqual(u'1.1', value)

    def test_dict_field_serialization_returns_dict(self):
        value = self.serialize('test_dict_field',
                               {'foo': 'bar', 'spam': 'eggs', '1': 1})
        self.assertTrue(isinstance(value, dict), 'Not a <dict>')
        self.assertEqual({u'foo': u'bar', u'spam': u'eggs', u'1': 1}, value)

    def test_float_field_serialization_returns_float(self):
        value = self.serialize('test_float_field', 1.5)
        self.assertTrue(isinstance(value, float), 'Not a <float>')
        self.assertEqual(1.5, value)

    def test_frozenset_field_serialization_returns_list(self):
        value = self.serialize('test_frozenset_field', frozenset([1, 2, 3]))
        self.assertTrue(isinstance(value, list), 'Not a <list>')
        self.assertEqual([1, 2, 3], sorted(value))

    def test_int_field_serialization_returns_int(self):
        value = self.serialize('test_int_field', 500)
        self.assertTrue(isinstance(value, int), 'Not an <int>')
        self.assertEqual(500, value)

    def test_list_field_serialization_returns_list(self):
        value = self.serialize('test_list_field', [1, 'two', 3])
        self.assertTrue(isinstance(value, list), 'Not a <list>')
        self.assertEqual([1, u'two', 3], value)

    def test_set_field_serialization_returns_list(self):
        value = self.serialize('test_set_field', set(['a', 'b', 'c']))
        self.assertTrue(isinstance(value, list), 'Not a <list>')
        self.assertEqual([u'a', u'b', u'c'], sorted(value))

    def test_text_field_serialization_returns_unicode(self):
        value = self.serialize('test_text_field', u'Käfer')
        self.assertTrue(isinstance(value, six.text_type), 'Not an <unicode>')
        self.assertEqual(u'Käfer', value)

    def test_textline_field_serialization_returns_unicode(self):
        value = self.serialize('test_textline_field', u'Käfer')
        self.assertTrue(isinstance(value, six.text_type), 'Not an <unicode>')
        self.assertEqual(u'Käfer', value)

    def test_time_field_serialization_returns_unicode(self):
        value = self.serialize('test_time_field', time(14, 15, 33))
        self.assertTrue(isinstance(value, six.text_type), 'Not an <unicode>')
        self.assertEqual(u'14:15:33', value)

    def test_timedelta_field_serialization_returns_float(self):
        value = self.serialize('test_timedelta_field', timedelta(0.01))
        self.assertTrue(isinstance(value, float), 'Not a <float>')
        self.assertEqual(864.0, value)

    def test_richtext_field_serialization_returns_dict(self):
        value = self.serialize('test_richtext_field', RichTextValue(
            raw=u'<p>Some Text</p>', mimeType='text/html',
            outputMimeType='text/html'))
        self.assertTrue(isinstance(value, dict), 'Not a <dict>')
        self.assertEqual({
            u'content-type': u'text/html',
            u'data': u'<p>Some Text</p>',
            u'encoding': u'utf-8'}, value)

    def test_namedfile_field_serialization_returns_dict(self):
        value = self.serialize(
            'test_namedfile_field',
            NamedFile(data=u'Spam and eggs', contentType=u'text/plain',
                      filename=u'test.txt'))
        self.assertTrue(isinstance(value, dict), 'Not a <dict>')
        download_url = u'/'.join([
            self.doc1.absolute_url(),
            u'@@download/test_namedfile_field'])
        self.assertEqual(
            {u'filename': u'test.txt',
             u'content-type': u'text/plain',
             u'size': 13,
             u'download': download_url},
            value)

    def test_namedimage_field_serialization_returns_dict(self):
        image_file = os.path.join(os.path.dirname(__file__), u'1024x768.gif')
        with open(image_file, 'rb') as f:
            image_data = f.read()
        fn = 'test_namedimage_field'
        with patch.object(storage, 'uuid4', return_value='uuid_1'):
            value = self.serialize(
                fn,
                NamedImage(
                    data=image_data,
                    contentType=u'image/gif',
                    filename=u'1024x768.gif'
                )
            )
            self.assertTrue(isinstance(value, dict), 'Not a <dict>')

            scale_url_uuid = 'uuid_1'
            obj_url = self.doc1.absolute_url()
            download_url = u'{}/@@images/{}.{}'.format(
                obj_url, scale_url_uuid, GIF_SCALE_FORMAT
            )
            scales = {
                u'listing': {
                    u'download': download_url,
                    u'width': 16,
                    u'height': 12},
                u'icon': {
                    u'download': download_url,
                    u'width': 32,
                    u'height': 24},
                u'tile': {
                    u'download': download_url,
                    u'width': 64,
                    u'height': 48},
                u'thumb': {
                    u'download': download_url,
                    u'width': 128,
                    u'height': 96},
                u'mini': {
                    u'download': download_url,
                    u'width': 200,
                    u'height': 150},
                u'preview': {
                    u'download': download_url,
                    u'width': 400,
                    u'height': 300},
                u'large': {
                    u'download': download_url,
                    u'width': 768,
                    u'height': 576},
            }
            self.assertEqual({
                u'filename': u'1024x768.gif',
                u'content-type': u'image/gif',
                u'size': 1514,
                u'download': download_url,
                u'width': 1024,
                u'height': 768,
                u'scales': scales},
                value)

    def test_namedblobfile_field_serialization_returns_dict(self):
        value = self.serialize(
            'test_namedblobfile_field',
            NamedBlobFile(data=u'Spam and eggs', contentType=u'text/plain',
                          filename=u'test.txt'))
        self.assertTrue(isinstance(value, dict), 'Not a <dict>')

        download_url = u'/'.join([
            self.doc1.absolute_url(),
            u'@@download/test_namedblobfile_field'])
        self.assertEqual(
            {u'filename': u'test.txt',
             u'content-type': u'text/plain',
             u'size': 13,
             u'download': download_url},
            value)

    def test_namedblobimage_field_serialization_returns_dict(self):
        image_file = os.path.join(os.path.dirname(__file__), u'1024x768.gif')
        with open(image_file, 'rb') as f:
            image_data = f.read()
        fn = 'test_namedblobimage_field'
        with patch.object(storage, 'uuid4', return_value='uuid_1'):
            value = self.serialize(
                fn,
                NamedBlobImage(
                    data=image_data,
                    contentType=u'image/gif',
                    filename=u'1024x768.gif'
                )
            )
            self.assertTrue(isinstance(value, dict), 'Not a <dict>')

            scale_url_uuid = 'uuid_1'
            obj_url = self.doc1.absolute_url()
            download_url = u'{}/@@images/{}.{}'.format(
                obj_url, scale_url_uuid, GIF_SCALE_FORMAT
            )
            scales = {
                u'listing': {
                    u'download': download_url,
                    u'width': 16,
                    u'height': 12},
                u'icon': {
                    u'download': download_url,
                    u'width': 32,
                    u'height': 24},
                u'tile': {
                    u'download': download_url,
                    u'width': 64,
                    u'height': 48},
                u'thumb': {
                    u'download': download_url,
                    u'width': 128,
                    u'height': 96},
                u'mini': {
                    u'download': download_url,
                    u'width': 200,
                    u'height': 150},
                u'preview': {
                    u'download': download_url,
                    u'width': 400,
                    u'height': 300},
                u'large': {
                    u'download': download_url,
                    u'width': 768,
                    u'height': 576},
            }
            self.assertEqual({
                u'filename': u'1024x768.gif',
                u'content-type': u'image/gif',
                u'size': 1514,
                u'download': download_url,
                u'width': 1024,
                u'height': 768,
                u'scales': scales},
                value)

    def test_relationchoice_field_serialization_returns_summary_dict(self):
        doc2 = self.portal[self.portal.invokeFactory(
            'DXTestDocument', id='doc2',
            title='Referenceable Document',
            description='Description 2',
        )]
        value = self.serialize('test_relationchoice_field', doc2)
        self.assertEqual(
            {'@id': 'http://nohost/plone/doc2',
             '@type': 'DXTestDocument',
             'title': 'Referenceable Document',
             'description': 'Description 2',
             'review_state': 'private'
             },
            value)

    def test_relationlist_field_serialization_returns_list(self):
        doc2 = self.portal[self.portal.invokeFactory(
            'DXTestDocument', id='doc2',
            title='Referenceable Document',
            description='Description 2',
        )]
        doc3 = self.portal[self.portal.invokeFactory(
            'DXTestDocument', id='doc3',
            title='Referenceable Document',
            description='Description 3',
        )]
        value = self.serialize('test_relationlist_field', [doc2, doc3])
        self.assertTrue(isinstance(value, list), 'Not a <list>')
        self.assertEqual([
            {'@id': 'http://nohost/plone/doc2',
             '@type': 'DXTestDocument',
             'title': 'Referenceable Document',
             'description': 'Description 2',
             'review_state': 'private'

             },
            {'@id': 'http://nohost/plone/doc3',
             '@type': 'DXTestDocument',
             'title': 'Referenceable Document',
             'description': 'Description 3',
             'review_state': 'private'
             }],
            value)


class TestDexterityFieldSerializers(TestCase):

    def default_field_serializer(self):
        verifyClass(IFieldSerializer, DefaultFieldSerializer)
