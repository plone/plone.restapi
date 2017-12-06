# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
from plone import namedfile
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from pytz import timezone

from plone.restapi.tests.dxtypes import IDXTestDocumentSchema
from zope.component import getMultiAdapter
from zope.schema._bootstrapinterfaces import RequiredMissing
from zope.schema.interfaces import ValidationError

import unittest


class RequiredField(object):
    """Context manager that will make a field required and back to old state.
    """
    def __init__(self, field):
        self.field = field
        self.old_state = field.required

    def __enter__(self):
        self.field.required = True

    def __exit__(self, *args, **kwargs):
        self.field.required = self.old_state


class TestDXFieldDeserializer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.portal.invokeFactory(
            'DXTestDocument', id='doc1', title='Test Document')

    def deserialize(self, fieldname, value):
        for schema in iterSchemata(self.portal.doc1):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        deserializer = getMultiAdapter((field, self.portal.doc1, self.request),
                                       IFieldDeserializer)
        return deserializer(value)

    def test_ascii_deserialization_returns_bytestring(self):
        value = self.deserialize('test_ascii_field', u'Foo')
        self.assertTrue(isinstance(value, str), 'Not a <str>')
        self.assertEqual('Foo', value)

    def test_asciiline_deserialization_returns_bytestring(self):
        value = self.deserialize('test_asciiline_field', u'Foo')
        self.assertTrue(isinstance(value, str), 'Not a <str>')
        self.assertEqual('Foo', value)

    def test_bool_deserialization_returns_true(self):
        value = self.deserialize('test_bool_field', True)
        self.assertTrue(isinstance(value, bool), 'Not a <bool>')
        self.assertEqual(True, value)

    def test_bool_deserialization_returns_false(self):
        value = self.deserialize('test_bool_field', False)
        self.assertTrue(isinstance(value, bool), 'Not a <bool>')
        self.assertEqual(False, value)

    def test_bytes_deserialization_returns_bytestring(self):
        value = self.deserialize('test_bytes_field', u'Foo')
        self.assertTrue(isinstance(value, str), 'Not a <str>')
        self.assertEqual('Foo', value)

    def test_bytesline_deserialization_returns_bytestring(self):
        value = self.deserialize('test_bytesline_field', u'Foo')
        self.assertTrue(isinstance(value, str), 'Not a <str>')
        self.assertEqual('Foo', value)

    def test_choice_deserialization_returns_vocabulary_item(self):
        value = self.deserialize('test_choice_field', u'bar')
        self.assertTrue(isinstance(value, unicode), 'Not an <unicode>')
        self.assertEqual(u'bar', value)

    def test_date_deserialization_returns_date(self):
        value = self.deserialize('test_date_field', u'2015-12-20')
        self.assertTrue(isinstance(value, date))
        self.assertEqual(date(2015, 12, 20), value)

    def test_datetime_deserialization_returns_datetime(self):
        value = self.deserialize('test_datetime_field',
                                 u'2015-12-20T10:39:54.361Z')
        self.assertTrue(isinstance(value, datetime), 'Not a <datetime>')
        self.assertEqual(datetime(2015, 12, 20, 10, 39, 54, 361000), value)

    def test_datetime_deserialization_handles_timezone(self):
        value = self.deserialize('test_datetime_field',
                                 u'2015-12-20T10:39:54.361+01')
        self.assertEqual(datetime(2015, 12, 20, 9, 39, 54, 361000), value)

    def test_datetime_with_tz_deserialization_keeps_timezone(self):
        value = self.deserialize('test_datetime_tz_field',
                                 u'2015-12-20T10:39:54.361+01')
        self.assertEqual(timezone("Europe/Zurich").localize(
            datetime(2015, 12, 20, 10, 39, 54, 361000)), value)

    def test_datetime_with_tz_deserialization_converts_timezone(self):
        value = self.deserialize('test_datetime_tz_field',
                                 u'2015-12-20T10:39:54.361-04')
        self.assertEqual(timezone("Europe/Zurich").localize(
            datetime(2015, 12, 20, 15, 39, 54, 361000)), value)

    def test_datetime_with_tz_deserialization_adds_timezone(self):
        value = self.deserialize('test_datetime_tz_field',
                                 u'2015-12-20T10:39:54.361')
        self.assertEqual(timezone("Europe/Zurich").localize(
            datetime(2015, 12, 20, 11, 39, 54, 361000)), value)

    def test_datetime_with_tz_deserialization_handles_dst(self):
        value = self.deserialize('test_datetime_tz_field',
                                 u'2015-05-20T10:39:54.361+02')
        self.assertEqual(timezone("Europe/Zurich").localize(
            datetime(2015, 05, 20, 10, 39, 54, 361000)), value)

    def test_datetime_deserialization_none(self):
        # Make sure we don't construct a datetime out of nothing
        value = self.deserialize('test_datetime_field', None)
        self.assertEqual(value, None)

    def test_datetime_deserialization_required(self):
        field_name = 'test_datetime_field'
        field = IDXTestDocumentSchema.get(field_name)
        with RequiredField(field):
            with self.assertRaises(RequiredMissing):
                self.deserialize(field_name, None)

    def test_decimal_deserialization_returns_decimal(self):
        value = self.deserialize('test_decimal_field', u'1.1')
        self.assertTrue(isinstance(value, Decimal), 'Not a <Decimal>')
        self.assertEqual(Decimal('1.1'), value)

    def test_dict_deserialization_returns_dict(self):
        value = self.deserialize('test_dict_field', {u'key': u'value'})
        self.assertTrue(isinstance(value, dict), 'Not a <dict>')
        self.assertEqual({u'key': u'value'}, value)

    def test_float_deserialization_returns_float(self):
        value = self.deserialize('test_float_field', 1.0)
        self.assertTrue(isinstance(value, float), 'Not a <float>')
        self.assertEqual(1.0, value)

    def test_frozenset_deserialization_returns_frozenset(self):
        value = self.deserialize('test_frozenset_field', [u'foo', u'bar'])
        self.assertTrue(isinstance(value, frozenset), 'Not a <frozenset>')
        self.assertEqual(frozenset([u'foo', u'bar']), value)

    def test_int_deserialization_returns_int(self):
        value = self.deserialize('test_int_field', 22)
        self.assertTrue(isinstance(value, int), 'Not an <int>')
        self.assertEqual(22, value)

    def test_list_deserialization_returns_list(self):
        value = self.deserialize('test_list_field', [1, 2, 3])
        self.assertTrue(isinstance(value, list), 'Not a <list>')
        self.assertEqual([1, 2, 3], value)

    def test_set_deserialization_returns_set(self):
        value = self.deserialize('test_set_field', [1, 2, 3])
        self.assertTrue(isinstance(value, set), 'Not a <set>')
        self.assertEqual(set([1, 2, 3]), value)

    def test_text_deserialization_returns_unicode(self):
        value = self.deserialize('test_text_field', u'Foo')
        self.assertTrue(isinstance(value, unicode), 'Not an <unicode>')
        self.assertEqual(u'Foo', value)

    def test_textline_deserialization_returns_unicode(self):
        value = self.deserialize('test_textline_field', u'Foo')
        self.assertTrue(isinstance(value, unicode), 'Not an <unicode>')
        self.assertEqual(u'Foo', value)

    def test_time_deserialization_returns_time(self):
        value = self.deserialize('test_time_field', u'10:39:54.361Z')
        self.assertTrue(isinstance(value, time), 'Not a <time>')
        self.assertEqual(time(10, 39, 54, 361000), value)

    def test_timedelta_deserialization_returns_timedela(self):
        value = self.deserialize('test_timedelta_field', 3600.0)
        self.assertTrue(isinstance(value, timedelta), 'Not a <timedelta>')
        self.assertEqual(timedelta(seconds=3600), value)

    def test_tuple_deserialization_returns_tuple(self):
        value = self.deserialize('test_tuple_field', [1, 2, 3])
        self.assertTrue(isinstance(value, tuple), 'Not a <tuple>')
        self.assertEqual((1, 2, 3), value)

    def test_nested_list_deserialization_returns_nested_list(self):
        value = self.deserialize('test_nested_list_field',
                                 [[1, u'foo'], [2, u'bar']])
        self.assertTrue(isinstance(value, list), 'Not a <list>')
        self.assertTrue(isinstance(value[0], tuple), 'Not a <tuple>')
        self.assertTrue(isinstance(value[1], tuple), 'Not a <tuple>')

    def test_nested_dict_deserialization_returns_nested_dict(self):
        value = self.deserialize(
            'test_nested_dict_field',
            {u'1': [u'foo', u'bar'], u'2': [u'spam', u'eggs']})
        self.assertTrue(isinstance(value, dict), 'Not a <dict>')
        self.assertIn('1', value)
        self.assertTrue(isinstance(value['1'], tuple), 'Not a <tuple>')
        self.assertIn('2', value)
        self.assertTrue(isinstance(value['2'], tuple), 'Not a <tuple>')

    def test_richtext_deserialization_from_unicode_returns_richtext(self):
        value = self.deserialize('test_richtext_field', u'<p>a paragraph</p>')
        self.assertTrue(isinstance(value, RichTextValue),
                        'Not a <RichTextValue>')
        self.assertEqual(u'<p>a paragraph</p>', value.raw)

    def test_richtext_deserialization_from_dict_returns_richtext(self):
        value = self.deserialize('test_richtext_field', {
            u'data': u'Some text',
        })
        self.assertTrue(isinstance(value, RichTextValue),
                        'Not a <RichTextValue>')
        self.assertEqual(u'Some text', value.raw)

    def test_richtext_deserialization_sets_mime_type(self):
        value = self.deserialize('test_richtext_field', {
            u'data': u'Some text',
            u'content-type': u'text/plain',
        })
        self.assertEqual('text/plain', value.mimeType)

    def test_richtext_deserialization_sets_encoding(self):
        value = self.deserialize('test_richtext_field', {
            u'data': u'Some text',
            u'encoding': u'latin1',
        })
        self.assertEqual('latin1', value.encoding)

    def test_namedfield_deserialization_decodes_value(self):
        value = self.deserialize('test_namedfile_field', {
            u'data': u'U3BhbSBhbmQgZWdncyE=',
            u'encoding': u'base64',
        })
        self.assertEquals('Spam and eggs!', value.data)

    def test_namedfield_deserialization_sets_content_type(self):
        value = self.deserialize('test_namedfile_field', {
            u'data': u'Spam and eggs!',
            u'content-type': u'text/plain',
        })
        self.assertEqual('text/plain', value.contentType)

    def test_namedfield_deserialization_sets_filename(self):
        value = self.deserialize('test_namedfile_field', {
            u'data': u'Spam and eggs!',
            u'filename': u'doc.txt',
        })
        self.assertEqual('doc.txt', value.filename)

    def test_namedfile_deserialization_returns_namedfile(self):
        value = self.deserialize('test_namedfile_field', {
            u'data': u'Spam and eggs!',
        })
        self.assertTrue(isinstance(value, namedfile.NamedFile),
                        'Not a <NamedFile>')
        self.assertEqual('Spam and eggs!', value.data)

    def test_namedimage_deserialization_returns_namedimage(self):
        value = self.deserialize('test_namedimage_field', {
            u'data': u'R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=',
            u'encoding': u'base64',
            u'content-type': u'image/gif',
        })
        self.assertTrue(isinstance(value, namedfile.NamedImage),
                        'Not a <NamedImage>')
        self.assertTrue(value.data.startswith('GIF89a'))

    def test_namedblobfile_deserialization_returns_namedblobfile(self):
        value = self.deserialize('test_namedblobfile_field', {
            u'data': u'Spam and eggs!',
        })
        self.assertTrue(isinstance(value, namedfile.NamedBlobFile),
                        'Not a <NamedBlobFile>')
        self.assertEqual('Spam and eggs!', value.data)

    def test_namedblobimage_deserialization_returns_namedblobimage(self):
        value = self.deserialize('test_namedblobimage_field', {
            u'data': u'R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=',
            u'encoding': u'base64',
            u'content-type': u'image/gif',
        })
        self.assertTrue(isinstance(value, namedfile.NamedBlobImage),
                        'Not a <NamedBlobImage>')
        self.assertTrue(value.data.startswith('GIF89a'))

    def test_namedblobimage_deserialization_fed_with_null_removes_image(self):
        # null in json translates to None in python.
        value = self.deserialize('test_namedblobimage_field', None)
        self.assertFalse(value)

    def test_namedblobfile_deserialization_fed_with_null_removes_file(self):
        # null in json translates to None in python.
        value = self.deserialize('test_namedblobfile_field', None)
        self.assertFalse(value)

    def test_namedblobfile_deserialize_required(self):
        field_name = 'test_namedblobfile_field'
        field = IDXTestDocumentSchema.get(field_name)
        with RequiredField(field):
            with self.assertRaises(RequiredMissing):
                self.deserialize(field_name, None)

    def test_namedblobimage_deserialize_required(self):
        field_name = 'test_namedblobimage_field'
        field = IDXTestDocumentSchema.get(field_name)
        with RequiredField(field):
            with self.assertRaises(RequiredMissing):
                self.deserialize(field_name, None)

    def test_relationchoice_deserialization_from_uid_returns_document(self):
        doc2 = self.portal[self.portal.invokeFactory(
            'DXTestDocument', id='doc2', title='Referenceable Document')]
        value = self.deserialize('test_relationchoice_field',
                                 unicode(doc2.UID()))
        self.assertEqual(doc2, value)

    def test_relationchoice_deserialization_from_url_returns_document(self):
        doc2 = self.portal[self.portal.invokeFactory(
            'DXTestDocument', id='doc2', title='Referenceable Document')]
        value = self.deserialize('test_relationchoice_field',
                                 unicode(doc2.absolute_url()))
        self.assertEqual(doc2, value)

    def test_relationchoice_deserialization_from_path_returns_document(self):
        doc2 = self.portal[self.portal.invokeFactory(
            'DXTestDocument', id='doc2', title='Referenceable Document')]
        value = self.deserialize('test_relationchoice_field', u'/doc2')
        self.assertEqual(doc2, value)

    def test_relationlist_deserialization_returns_list_of_documents(self):
        doc2 = self.portal[self.portal.invokeFactory(
            'DXTestDocument', id='doc2', title='Referenceable Document')]
        doc3 = self.portal[self.portal.invokeFactory(
            'DXTestDocument', id='doc3', title='Referenceable Document')]
        value = self.deserialize('test_relationlist_field',
                                 [unicode(doc2.UID()), unicode(doc3.UID())])
        self.assertTrue(isinstance(value, list), 'Not a <list>')
        self.assertEqual(doc2, value[0])
        self.assertEqual(doc3, value[1])

    def test_default_deserializer_validates_value(self):
        with self.assertRaises(ValidationError):
            self.deserialize('test_maxlength_field', u'01234567890')

    def test_datetime_deserializer_handles_invalid_value(self):
        with self.assertRaises(ValueError) as cm:
            self.deserialize('test_datetime_field',
                             u'2015-15-15T10:39:54.361Z')
        self.assertEqual(u'Invalid date: 2015-15-15T10:39:54.361Z',
                         cm.exception.message)

    def test_datetime_deserializer_validates_value(self):
        with self.assertRaises(ValidationError):
            self.deserialize('test_datetime_min_field',
                             u'1999-12-20T10:39:54.361Z')

    def test_collection_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize('test_list_value_type_field', [1, '2', 3])
        self.assertEqual(u'Wrong contained type', cm.exception.doc())

    def test_dict_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize('test_dict_key_type_field', {'k': 'v'})
        self.assertEqual(u'Wrong contained type', cm.exception.doc())

    def test_time_deserializer_handles_invalid_value(self):
        with self.assertRaises(ValueError) as cm:
            self.deserialize('test_time_field',
                             u'midnight')
        self.assertEqual(u'Invalid time: midnight',
                         cm.exception.message)

    def test_time_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize('test_time_min_field', u'00:39:54.361Z')
        self.assertEqual(u'Value is too small',
                         cm.exception.doc())

    def test_timedelta_deserializer_handles_invalid_value(self):
        with self.assertRaises(ValueError) as cm:
            self.deserialize('test_timedelta_field',
                             u'2h')
        self.assertEqual(
            u'unsupported type for timedelta seconds component: unicode',
            cm.exception.message)

    def test_timedelta_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize('test_timedelta_min_field', 50)
        self.assertEqual(u'Value is too small',
                         cm.exception.doc())

    def test_namedfield_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize('test_namedimage_field', {
                u'data': u'Spam and eggs!',
                u'content-type': u'text/plain',
            })
        self.assertEqual(u'Invalid image file', cm.exception.doc())

    def test_namedfield_deserializer_download(self):
        # Handle when we post back the GET results.
        # This then has a 'download' key, and not a 'data' key.

        self.deserialize('test_namedfile_field', {
            u'download': u'some download link',
            u'content-type': u'text/plain',
        })

    def test_richtextfield_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize('test_richtext_field', {
                u'data': u'Spam and eggs!',
                u'content-type': u'text/xml',
            })
        self.assertEqual(u'Object is of wrong type.', cm.exception.doc())

    def test_relationchoicefield_deserializer_validates_value(self):
        self.portal[self.portal.invokeFactory(
            'DXTestDocument', id='doc3', title='Referenceable Document')]
        with self.assertRaises(ValidationError) as cm:
            self.deserialize('test_relationchoice_field', u'/doc3')
        self.assertEqual(u'Constraint not satisfied', cm.exception.doc())

    def test_deserialize_with_context_bound_vocabulary(self):
        value = self.deserialize(
            'test_list_choice_with_context_vocabulary_field',
            [u'portal_catalog'])
        self.assertEqual([u'portal_catalog'], value)

    def test_textline_deserializer_strips_value(self):
        value = self.deserialize('test_textline_field', u'  aa  ')
        self.assertEquals(value, 'aa')
