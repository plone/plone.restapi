# -*- coding: utf-8 -*-
from DateTime import DateTime
from mock import patch
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.testing import HAS_AT
from plone.restapi.testing import PLONE_RESTAPI_AT_INTEGRATION_TESTING
from plone.restapi.testing import PLONE_VERSION
from plone.scale import storage
from zope.component import getMultiAdapter

import os
import six
import unittest


if PLONE_VERSION.base_version >= "5.1":
    GIF_SCALE_FORMAT = "png"
else:
    GIF_SCALE_FORMAT = "jpeg"


class TestATFieldSerializer(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        if not HAS_AT:
            raise unittest.SkipTest("Skip tests if Archetypes is not present")
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "ATTestDocument", id="doc1", title="Test Document"
            )
        ]

    def serialize(self, fieldname, value, **kwargs):
        field = self.doc1.getField(fieldname)
        mutator = field.getMutator(self.doc1)
        mutator(value, **kwargs)
        serializer = getMultiAdapter((field, self.doc1, self.request), IFieldSerializer)
        return serializer()

    def test_string_field_serialization_returns_unicode(self):
        value = self.serialize("testStringField", u"Käfer")
        self.assertTrue(isinstance(value, six.text_type), "Not an <unicode>")
        self.assertEqual(u"Käfer", value)

    def test_boolean_field_serialization_returns_true(self):
        value = self.serialize("testBooleanField", True)
        self.assertTrue(isinstance(value, bool), "Not a <bool>")
        self.assertTrue(value)

    def test_boolean_field_serialization_returns_false(self):
        value = self.serialize("testBooleanField", False)
        self.assertTrue(isinstance(value, bool), "Not a <bool>")
        self.assertFalse(value)

    def test_integer_field_serialization_returns_int(self):
        value = self.serialize("testIntegerField", 333)
        self.assertTrue(isinstance(value, int), "Not an <int>")
        self.assertEqual(333, value)

    def test_float_field_serialization_returns_float(self):
        value = self.serialize("testFloatField", 1.5)
        self.assertTrue(isinstance(value, float), "Not an <float>")
        self.assertEqual(1.5, value)

    def test_fixedpoint_field_serialization_returns_unicode(self):
        value = self.serialize("testFixedPointField", u"1.11")
        self.assertTrue(isinstance(value, six.text_type), "Not an <unicode>")
        self.assertEqual(u"1.11", value)

    def test_datetime_field_serialization_returns_unicode(self):
        value = self.serialize(
            "testDateTimeField", DateTime("2016-01-21T01:14:48+00:00")
        )
        self.assertTrue(isinstance(value, six.text_type), "Not an <unicode>")
        self.assertEqual(u"2016-01-21T01:14:48+00:00", value)

    def test_lines_field_serialization_returns_list(self):
        value = self.serialize("testLinesField", u"foo\nbar")
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual([u"foo", u"bar"], value)

    def test_file_field_serialization_returns_dict(self):
        value = self.serialize(
            "testFileField", "spam and eggs", filename="spam.txt", mimetype="text/plain"
        )
        self.assertTrue(isinstance(value, dict), "Not a <dict>")

        url = u"http://nohost/plone/doc1/@@download/testFileField"
        self.assertEqual(
            {
                u"filename": u"spam.txt",
                u"content-type": u"text/plain",
                u"size": 13,
                u"download": url,
            },
            value,
        )

    def test_text_field_serialization_returns_dict(self):
        value = self.serialize("testTextField", "<p>spam and eggs</p>")
        self.assertTrue(isinstance(value, dict), "Not a <dict>")
        self.assertDictEqual(
            {"content-type": u"text/plain", "data": u" spam and eggs "}, value
        )

    def test_image_field_serialization_returns_dict(self):
        image_file = os.path.join(os.path.dirname(__file__), u"1024x768.gif")
        with open(image_file, "rb") as f:
            image_data = f.read()
        fn = "testImageField"
        with patch.object(storage, "uuid4", return_value="uuid_1"):
            value = self.serialize(
                fn, image_data, filename="1024x768.gif", mimetype="image/gif"
            )
            self.assertTrue(isinstance(value, dict), "Not a <dict>")

            self.maxDiff = 99999
            obj_url = self.doc1.absolute_url()
            scale_url_uuid = "uuid_1"
            download_url = u"{}/@@images/{}.{}".format(
                obj_url, scale_url_uuid, GIF_SCALE_FORMAT
            )
            scales = {
                u"listing": {u"download": download_url, u"width": 16, u"height": 12},
                u"icon": {u"download": download_url, u"width": 32, u"height": 24},
                u"tile": {u"download": download_url, u"width": 64, u"height": 48},
                u"thumb": {u"download": download_url, u"width": 80, u"height": 60},
                u"mini": {u"download": download_url, u"width": 200, u"height": 150},
                u"preview": {u"download": download_url, u"width": 400, u"height": 300},
                u"large": {u"download": download_url, u"width": 768, u"height": 576},
            }
            self.assertEqual(
                {
                    u"filename": u"1024x768.gif",
                    u"content-type": u"image/gif",
                    u"size": 1514,
                    u"download": download_url,
                    u"width": 1024,
                    u"height": 768,
                    u"scales": scales,
                },
                value,
            )

    def test_blob_field_serialization_returns_dict(self):
        value = self.serialize(
            "testBlobField", "spam and eggs", filename="spam.txt", mimetype="text/plain"
        )
        self.assertTrue(isinstance(value, dict), "Not an <dict>")
        url = u"http://nohost/plone/doc1/@@download/testBlobField"
        self.assertEqual(
            {
                u"filename": "spam.txt",
                u"size": 13,
                u"content-type": "text/plain",
                u"download": url,
            },
            value,
        )

    def test_blobfile_field_serialization_returns_dict(self):
        value = self.serialize(
            "testBlobFileField",
            "spam and eggs",
            filename="spam.txt",
            mimetype="text/plain",
        )

        self.assertTrue(isinstance(value, dict), "Not a <dict>")
        url = u"http://nohost/plone/doc1/@@download/testBlobFileField"
        self.assertEqual(
            {
                u"filename": "spam.txt",
                u"content-type": u"text/plain",
                u"size": 13,
                u"download": url,
            },
            value,
        )

    def test_blobimage_field_serialization_returns_dict(self):
        image_file = os.path.join(os.path.dirname(__file__), u"1024x768.gif")
        with open(image_file, "rb") as f:
            image_data = f.read()
        fn = "testBlobImageField"
        with patch.object(storage, "uuid4", return_value="uuid_1"):
            value = self.serialize(
                fn, image_data, filename="1024x768.gif", mimetype="image/gif"
            )
            self.assertTrue(isinstance(value, dict), "Not a <dict>")
            scale_url_uuid = "uuid_1"
            obj_url = self.doc1.absolute_url()
            download_url = u"{}/@@images/{}.{}".format(
                obj_url, scale_url_uuid, GIF_SCALE_FORMAT
            )
            scales = {
                u"listing": {u"download": download_url, u"width": 16, u"height": 12},
                u"icon": {u"download": download_url, u"width": 32, u"height": 24},
                u"tile": {u"download": download_url, u"width": 64, u"height": 48},
                u"thumb": {u"download": download_url, u"width": 128, u"height": 96},
                u"mini": {u"download": download_url, u"width": 200, u"height": 150},
                u"preview": {u"download": download_url, u"width": 400, u"height": 300},
                u"large": {u"download": download_url, u"width": 768, u"height": 576},
            }
            self.assertEqual(
                {
                    u"filename": u"1024x768.gif",
                    u"content-type": u"image/gif",
                    u"size": 1514,
                    u"download": download_url,
                    u"width": 1024,
                    u"height": 768,
                    u"scales": scales,
                },
                value,
            )

    def test_query_field_serialization_returns_list(self):
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
        value = self.serialize("testQueryField", query_data)
        self.assertTrue(isinstance(value, list), "Not a list")
        self.assertEqual(value, query_data)

    def test_reference_field_serialization_returns_unicode(self):
        doc2 = self.portal[
            self.portal.invokeFactory(
                "ATTestDocument", id="doc2", title="Referenceable Document"
            )
        ]
        value = self.serialize("testReferenceField", doc2.UID())
        self.assertTrue(isinstance(value, six.text_type), "Not an <unicode>")
        self.assertEqual(u"http://nohost/plone/doc2", value)

    def test_reference_field_serialization_returns_list(self):
        doc2 = self.portal[
            self.portal.invokeFactory(
                "ATTestDocument", id="doc2", title="Referenceable Document"
            )
        ]
        doc3 = self.portal[
            self.portal.invokeFactory(
                "ATTestDocument", id="doc3", title="Referenceable Document"
            )
        ]
        value = self.serialize("testMVReferenceField", [doc2.UID(), doc3.UID()])
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual(
            [u"http://nohost/plone/doc2", u"http://nohost/plone/doc3"], sorted(value)
        )
