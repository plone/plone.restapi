# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.testing import PLONE_RESTAPI_AT_INTEGRATION_TESTING
from zope.component import getMultiAdapter

import unittest


class TestATFieldSerializer(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        self.doc1 = self.portal[self.portal.invokeFactory(
            'ATTestDocument', id='doc1', title='Test Document')]

    def serialize(self, fieldname, value, **kwargs):
        field = self.doc1.getField(fieldname)
        mutator = field.getMutator(self.doc1)
        mutator(value)
        serializer = getMultiAdapter((field, self.doc1, self.request),
                                     IFieldSerializer)
        return serializer()

    def test_string_field_serialization_returns_unicode(self):
        value = self.serialize('testStringField', u'Käfer')
        self.assertTrue(isinstance(value, unicode), 'Not an <unicode>')
        self.assertEqual(u'Käfer', value)

    def test_boolean_field_serialization_returns_true(self):
        value = self.serialize('testBooleanField', True)
        self.assertTrue(isinstance(value, bool), 'Not a <bool>')
        self.assertTrue(value)

    def test_boolean_field_serialization_returns_false(self):
        value = self.serialize('testBooleanField', False)
        self.assertTrue(isinstance(value, bool), 'Not a <bool>')
        self.assertFalse(value)

    def test_integer_field_serialization_returns_int(self):
        value = self.serialize('testIntegerField', 333)
        self.assertTrue(isinstance(value, int), 'Not an <int>')
        self.assertEqual(333, value)

    def test_float_field_serialization_returns_float(self):
        value = self.serialize('testFloatField', 1.5)
        self.assertTrue(isinstance(value, float), 'Not an <float>')
        self.assertEqual(1.5, value)

    def test_fixedpoint_field_serialization_returns_unicode(self):
        value = self.serialize('testFixedPointField', u'1.11')
        self.assertTrue(isinstance(value, unicode), 'Not an <unicode>')
        self.assertEqual(u'1.11', value)

    def test_datetime_field_serialization_returns_unicode(self):
        value = self.serialize('testDateTimeField',
                               DateTime('2016-01-21T01:14:48+00:00'))
        self.assertTrue(isinstance(value, unicode), 'Not an <unicode>')
        self.assertEqual(u'2016-01-21T01:14:48+00:00', value)

    def test_lines_field_serialization_returns_list(self):
        value = self.serialize('testLinesField', u'foo\nbar')
        self.assertTrue(isinstance(value, list), 'Not a <list>')
        self.assertEqual([u'foo', u'bar'], value)

    def test_file_field_serialization_returns_unicode(self):
        value = self.serialize('testFileField', 'spam and eggs',
                               filename='spam.txt', mimetype='text/plain')
        self.assertTrue(isinstance(value, unicode), 'Not an <unicode>')
        self.assertEqual(u'http://nohost/plone/doc1/@@download/testFileField',
                         value)

    def test_text_field_serialization_returns_dict(self):
        value = self.serialize('testTextField', '<p>spam and eggs</p>',
                               mimetype='text/html')
        self.assertTrue(isinstance(value, dict), 'Not a <dict>')
        self.assertDictEqual({
            'content-type': u'text/html',
            'data': u'<p>spam and eggs</p>'}, value)

    def test_image_field_serialization_returns_unicode(self):
        image_data = (
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00,\x00'
            '\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
        value = self.serialize('testImageField', image_data,
                               filename='image.gif', mimetype='image/gif')
        self.assertTrue(isinstance(value, unicode), 'Not an <unicode>')
        self.assertEqual(u'http://nohost/plone/doc1/@@images/testImageField',
                         value)

    def test_reference_field_serialization_returns_unicode(self):
        doc2 = self.portal[self.portal.invokeFactory(
            'ATTestDocument', id='doc2', title='Referenceable Document')]
        value = self.serialize('testReferenceField', doc2.UID())
        self.assertTrue(isinstance(value, unicode), 'Not an <unicode>')
        self.assertEqual(u'http://nohost/plone/doc2', value)

    def test_reference_field_serialization_returns_list(self):
        doc2 = self.portal[self.portal.invokeFactory(
            'ATTestDocument', id='doc2', title='Referenceable Document')]
        doc3 = self.portal[self.portal.invokeFactory(
            'ATTestDocument', id='doc3', title='Referenceable Document')]
        value = self.serialize('testMVReferenceField',
                               [doc2.UID(), doc3.UID()])
        self.assertTrue(isinstance(value, list), 'Not a <list>')
        self.assertEqual(
            [u'http://nohost/plone/doc2', u'http://nohost/plone/doc3'],
            sorted(value))
