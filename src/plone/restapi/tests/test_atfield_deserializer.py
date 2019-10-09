# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.testing import HAS_AT
from plone.restapi.testing import PLONE_RESTAPI_AT_INTEGRATION_TESTING
from zope.component import getMultiAdapter

import six
import unittest


class TestATFieldDeserializer(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        if not HAS_AT:
            raise unittest.SkipTest("Skip tests if Archetypes is not present")
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        self.portal.invokeFactory("ATTestDocument", id="doc1", title="Test Document")

    def deserialize(self, fieldname, value):
        field = self.portal.doc1.getField(fieldname)
        deserializer = getMultiAdapter(
            (field, self.portal.doc1, self.request), IFieldDeserializer
        )
        return deserializer(value)

    def test_string_field_deserialization_returns_string(self):
        value, kwargs = self.deserialize("testStringField", u"Käfer")
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertEqual(u"Käfer", value)

    def test_boolean_field_deserialization_returns_true(self):
        value, kwargs = self.deserialize("testBooleanField", True)
        self.assertTrue(isinstance(value, bool), "Not a <bool>")
        self.assertEqual(True, value)

    def test_boolean_field_deserialization_returns_false(self):
        value, kwargs = self.deserialize("testBooleanField", False)
        self.assertTrue(isinstance(value, bool), "Not a <bool>")
        self.assertEqual(False, value)

    def test_integer_field_deserialization_returns_integer_value(self):
        value, kwargs = self.deserialize("testIntegerField", 777)
        self.assertTrue(isinstance(value, int), "Not an <int>")
        self.assertEqual(777, value)

    def test_float_field_deserialization_returns_float_value(self):
        value, kwargs = self.deserialize("testFloatField", 1.5)
        self.assertTrue(isinstance(value, float), "Not a <float>")
        self.assertEqual(1.5, value)

    def test_fixedpoint_field_deserialization_returns_string(self):
        value, kwargs = self.deserialize("testFixedPointField", u"1.1")
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertEqual(u"1.1", value)

    def test_datetime_field_deserialization_returns_string(self):
        value, kwargs = self.deserialize(
            "testDateTimeField", u"2015-12-20T19:51:06.375Z"
        )
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertEqual(u"2015-12-20T19:51:06.375Z", value)

    def test_lines_field_deserialization_returns_string(self):
        value, kwargs = self.deserialize("testLinesField", u"line1\nline2")
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertEqual("line1\nline2", value)

    def test_lines_field_deserialization_returns_list(self):
        value, kwargs = self.deserialize("testLinesField", [u"line1", u"line2"])
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual([u"line1", u"line2"], value)

    def test_file_field_deserialization_returns_string(self):
        value, kwargs = self.deserialize("testFileField", u"Spam and eggs!")
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertEqual(u"Spam and eggs!", value)

    def test_file_field_deserialization_returns_decoded_value(self):
        value, kwargs = self.deserialize(
            "testFileField", {u"data": u"U3BhbSBhbmQgZWdncyE=", u"encoding": u"base64"}
        )
        self.assertTrue(isinstance(value, str), "Not a <str>")
        self.assertEqual("Spam and eggs!", value)

    def test_file_field_deserialization_returns_mimetype_and_filename(self):
        value, kwargs = self.deserialize(
            "testFileField",
            {
                u"data": u"Spam and eggs!",
                u"filename": "doc.txt",
                u"content-type": "text/plain",
            },
        )
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertEqual(u"Spam and eggs!", value)
        self.assertEqual("text/plain", kwargs[u"mimetype"])
        self.assertEqual("doc.txt", kwargs[u"filename"])

    def test_text_field_deserialization_returns_string(self):
        value, kwargs = self.deserialize("testTextField", u"Käfer")
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertEqual(u"Käfer", value)

    def test_text_field_deserialization_returns_mimetype(self):
        value, kwargs = self.deserialize(
            "testTextField", {u"data": u"Käfer", u"content-type": "text/html"}
        )
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertEqual(u"Käfer", value)
        self.assertEqual("text/html", kwargs[u"mimetype"])

    def test_image_field_deserialization_returns_mimetype_and_filename(self):
        value, kwargs = self.deserialize(
            "testImageField",
            {
                u"data": u"R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=",
                u"encoding": u"base64",
                u"filename": "image.gif",
                u"content-type": "image/gif",
            },
        )
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertTrue(value.startswith("GIF89a"))
        self.assertEqual("image/gif", kwargs[u"mimetype"])
        self.assertEqual("image.gif", kwargs[u"filename"])

    def test_blob_field_deserialization_returns_string(self):
        value, kwargs = self.deserialize("testBlobField", u"Spam and eggs!")
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertEqual(u"Spam and eggs!", value)

    def test_blob_field_deserialization_returns_mimetype_and_filename(self):
        value, kwargs = self.deserialize(
            "testBlobField",
            {
                u"data": u"Spam and eggs!",
                u"filename": "doc.txt",
                u"content-type": "text/plain",
            },
        )
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertEqual(u"Spam and eggs!", value)
        self.assertEqual("text/plain", kwargs[u"mimetype"])
        self.assertEqual("doc.txt", kwargs[u"filename"])

    def test_blobfile_field_deserialization_returns_mimetype_and_filename(self):
        value, kwargs = self.deserialize(
            "testBlobFileField",
            {
                u"data": u"Spam and eggs!",
                u"filename": "doc.txt",
                u"content-type": "text/plain",
            },
        )
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertEqual(u"Spam and eggs!", value)
        self.assertEqual("text/plain", kwargs[u"mimetype"])
        self.assertEqual("doc.txt", kwargs[u"filename"])

    def test_blobimage_field_deserialization_returns_mimetype_and_filename(self):
        value, kwargs = self.deserialize(
            "testBlobImageField",
            {
                u"data": u"R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=",
                u"encoding": u"base64",
                u"filename": "image.gif",
                u"content-type": "image/gif",
            },
        )
        self.assertTrue(isinstance(value, six.string_types), "Not a <basestring>")
        self.assertTrue(value.startswith("GIF89a"))
        self.assertEqual("image/gif", kwargs[u"mimetype"])
        self.assertEqual("image.gif", kwargs[u"filename"])

    def test_query_field_deserialization_requests_list(self):
        query_data = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": ["News Item"],
            },
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.path",
                "v": "/Plone/news",
            },
        ]
        value, kwargs = self.deserialize("testQueryField", query_data)
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual(value, query_data)

    def test_reference_field_deserialization_returns_uid_in_list(self):
        value, kwargs = self.deserialize(
            "testReferenceField", u"0fc0dac495034b869b3b90c9179499a9"
        )
        self.assertTrue(isinstance(value, list), "Not a <basestring>")
        self.assertEqual([u"0fc0dac495034b869b3b90c9179499a9"], value)

    def test_reference_field_deserialization_returns_uids(self):
        value, kwargs = self.deserialize(
            "testReferenceField",
            [u"0fc0dac495034b869b3b90c9179499a9", u"984c22058343453f997ef9e9de1e8136"],
        )
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertIn(u"0fc0dac495034b869b3b90c9179499a9", value)
        self.assertIn(u"984c22058343453f997ef9e9de1e8136", value)

    def test_reference_field_deserialization_returns_object_in_list(self):
        doc2 = self.portal[
            self.portal.invokeFactory(
                "ATTestDocument", id="doc2", title="Referenced Document"
            )
        ]
        value, kwargs = self.deserialize(
            "testReferenceField", six.text_type(doc2.absolute_url())
        )
        self.assertEqual(doc2, value[0])

    def test_reference_field_deserialization_returns_objects(self):
        doc2 = self.portal[
            self.portal.invokeFactory(
                "ATTestDocument", id="doc2", title="Referenced Document"
            )
        ]
        doc3 = self.portal[
            self.portal.invokeFactory(
                "ATTestDocument", id="doc3", title="Referenced Document"
            )
        ]
        value, kwargs = self.deserialize(
            "testReferenceField",
            [six.text_type(doc2.absolute_url()), six.text_type(doc3.absolute_url())],
        )
        self.assertEqual(doc2, value[0])
        self.assertEqual(doc3, value[1])
