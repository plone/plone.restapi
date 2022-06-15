from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
from importlib import import_module
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import iterSchemata
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.tests.helpers import patch_scale_uuid
from plone.uuid.interfaces import IUUID
from unittest import TestCase
from z3c.form.interfaces import IDataManager
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass

import os


HAS_PLONE_6 = getattr(
    import_module("Products.CMFPlone.factory"), "PLONE60MARKER", False
)


class TestDexterityFieldSerializing(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING
    maxDiff = None

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc1", title="Test Document"
            )
        ]

    def serialize(self, fieldname, value):
        for schema in iterSchemata(self.doc1):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        dm = getMultiAdapter((self.doc1, field), IDataManager)
        dm.set(value)
        serializer = getMultiAdapter((field, self.doc1, self.request), IFieldSerializer)
        return serializer()

    def test_ascii_field_serialization_returns_unicode(self):
        value = self.serialize("test_ascii_field", "foo")
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("foo", value)

    def test_asciiline_field_serialization_returns_unicode(self):
        value = self.serialize("test_asciiline_field", "foo")
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("foo", value)

    def test_bool_field_serialization_returns_true(self):
        value = self.serialize("test_bool_field", True)
        self.assertTrue(isinstance(value, bool), "Not a <bool>")
        self.assertEqual(True, value)

    def test_bool_field_serialization_returns_false(self):
        value = self.serialize("test_bool_field", False)
        self.assertTrue(isinstance(value, bool), "Not a <bool>")
        self.assertEqual(False, value)

    def test_bytes_field_serialization_returns_unicode(self):
        value = self.serialize("test_bytes_field", b"\xc3\xa4\xc3\xb6\xc3\xbc")
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("\xe4\xf6\xfc", value)

    def test_bytesline_field_serialization_returns_unicode(self):
        value = self.serialize("test_bytesline_field", b"\xc3\xa4\xc3\xb6\xc3\xbc")
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("\xe4\xf6\xfc", value)

    def test_choice_field_serialization_returns_vocabulary_term(self):
        value = self.serialize("test_choice_field", "foo")
        self.assertTrue(isinstance(value, dict))
        self.assertEqual({"token": "foo", "title": None}, value)

    def test_choice_field_with_vocabulary_serialization_returns_vocabulary_term(
        self,
    ):  # noqa
        value = self.serialize("test_choice_field_with_vocabulary", "value1")
        self.assertTrue(isinstance(value, dict))
        self.assertEqual({"token": "token1", "title": "title1"}, value)

    def test_date_field_serialization_returns_unicode(self):
        value = self.serialize("test_date_field", date(2015, 7, 15))
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("2015-07-15", value)

    def test_datetime_field_serialization_returns_unicode(self):
        value = self.serialize("test_datetime_field", datetime(2015, 6, 20, 13, 22, 4))
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("2015-06-20T13:22:04", value)

    def test_decimal_field_serialization_returns_unicode(self):
        value = self.serialize("test_decimal_field", Decimal("1.1"))
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("1.1", value)

    def test_dict_field_serialization_returns_dict(self):
        value = self.serialize(
            "test_dict_field", {"foo": "bar", "spam": "eggs", "1": 1}
        )
        self.assertTrue(isinstance(value, dict), "Not a <dict>")
        self.assertEqual({"foo": "bar", "spam": "eggs", "1": 1}, value)

    def test_float_field_serialization_returns_float(self):
        value = self.serialize("test_float_field", 1.5)
        self.assertTrue(isinstance(value, float), "Not a <float>")
        self.assertEqual(1.5, value)

    def test_frozenset_field_serialization_returns_list(self):
        value = self.serialize("test_frozenset_field", frozenset([1, 2, 3]))
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual([1, 2, 3], sorted(value))

    def test_int_field_serialization_returns_int(self):
        value = self.serialize("test_int_field", 500)
        self.assertTrue(isinstance(value, int), "Not an <int>")
        self.assertEqual(500, value)

    def test_list_field_serialization_returns_list(self):
        value = self.serialize("test_list_field", [1, "two", 3])
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual([1, "two", 3], value)

    def test_list_field_with_vocabulary_choice_serialization_returns_terms(self):
        value = self.serialize(
            "test_list_field_with_choice_with_vocabulary", ["value1", "value3"]
        )
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual(
            [
                {"token": "token1", "title": "title1"},
                {"token": "token3", "title": "title3"},
            ],
            value,
        )

    def test_list_field_with_vocabulary_choice_serialization_no_valid_term(self):
        value = self.serialize(
            "test_list_field_with_choice_with_vocabulary", ["value3", "value4"]
        )
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual(
            [{"token": "token3", "title": "title3"}],
            value,
        )

    def test_set_field_serialization_returns_list(self):
        value = self.serialize("test_set_field", {"a", "b", "c"})
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual(["a", "b", "c"], sorted(value))

    def test_set_field_with_vocabulary_choice_serialization_returns_terms(self):
        value = self.serialize(
            "test_set_field_with_choice_with_vocabulary", {"value1", "value3"}
        )
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual(
            [
                {"token": "token1", "title": "title1"},
                {"token": "token3", "title": "title3"},
            ],
            sorted(value, key=lambda x: x["token"]),
        )

    def test_text_field_serialization_returns_unicode(self):
        value = self.serialize("test_text_field", "Käfer")
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("Käfer", value)

    def test_textline_field_serialization_returns_unicode(self):
        value = self.serialize("test_textline_field", "Käfer")
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("Käfer", value)

    def test_time_field_serialization_returns_unicode(self):
        value = self.serialize("test_time_field", time(14, 15, 33))
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("14:15:33", value)

    def test_timedelta_field_serialization_returns_float(self):
        value = self.serialize("test_timedelta_field", timedelta(0.01))
        self.assertTrue(isinstance(value, float), "Not a <float>")
        self.assertEqual(864.0, value)

    def test_richtext_field_serialization_returns_dict(self):
        value = self.serialize(
            "test_richtext_field",
            RichTextValue(
                raw="<p>Some Text</p>",
                mimeType="text/html",
                outputMimeType="text/html",
            ),
        )
        self.assertTrue(isinstance(value, dict), "Not a <dict>")
        self.assertEqual(
            {
                "content-type": "text/html",
                "data": "<p>Some Text</p>",
                "encoding": "utf-8",
            },
            value,
        )

    def test_namedfile_field_serialization_returns_dict(self):
        value = self.serialize(
            "test_namedfile_field",
            NamedFile(
                data="Spam and eggs", contentType="text/plain", filename="test.txt"
            ),
        )
        self.assertTrue(isinstance(value, dict), "Not a <dict>")
        download_url = "/".join(
            [self.doc1.absolute_url(), "@@download/test_namedfile_field"]
        )
        self.assertEqual(
            {
                "filename": "test.txt",
                "content-type": "text/plain",
                "size": 13,
                "download": download_url,
            },
            value,
        )

    def test_namedblobfile_field_serialization_returns_dict(self):
        value = self.serialize(
            "test_namedblobfile_field",
            NamedBlobFile(
                data="Spam and eggs", contentType="text/plain", filename="test.txt"
            ),
        )
        self.assertTrue(isinstance(value, dict), "Not a <dict>")

        download_url = "/".join(
            [self.doc1.absolute_url(), "@@download/test_namedblobfile_field"]
        )
        self.assertEqual(
            {
                "filename": "test.txt",
                "content-type": "text/plain",
                "size": 13,
                "download": download_url,
            },
            value,
        )

    def test_relationchoice_field_serialization_returns_summary_dict(self):
        doc2 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument",
                id="doc2",
                title="Referenceable Document",
                description="Description 2",
            )
        ]
        value = self.serialize("test_relationchoice_field", doc2)
        self.assertEqual(
            {
                "@id": "http://nohost/plone/doc2",
                "@type": "DXTestDocument",
                "title": "Referenceable Document",
                "description": "Description 2",
                "review_state": "private",
            },
            value,
        )

    def test_relationlist_field_serialization_returns_list(self):
        doc2 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument",
                id="doc2",
                title="Referenceable Document",
                description="Description 2",
            )
        ]
        doc3 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument",
                id="doc3",
                title="Referenceable Document",
                description="Description 3",
            )
        ]
        value = self.serialize("test_relationlist_field", [doc2, doc3])
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual(
            [
                {
                    "@id": "http://nohost/plone/doc2",
                    "@type": "DXTestDocument",
                    "title": "Referenceable Document",
                    "description": "Description 2",
                    "review_state": "private",
                },
                {
                    "@id": "http://nohost/plone/doc3",
                    "@type": "DXTestDocument",
                    "title": "Referenceable Document",
                    "description": "Description 3",
                    "review_state": "private",
                },
            ],
            value,
        )

    def test_remoteurl_field_in_links_get_converted(self):
        link = self.portal[
            self.portal.invokeFactory(
                "Link",
                id="link",
                title="Test Link",
            )
        ]
        field = None
        for schema in iterSchemata(link):
            if "remoteUrl" in schema:
                field = schema.get("remoteUrl")
                break
        dm = getMultiAdapter((link, field), IDataManager)
        serializer = getMultiAdapter((field, link, self.request), IFieldSerializer)

        dm.set("http://www.plone.com")
        self.assertEqual(serializer(), "http://www.plone.com")

        doc_uuid = IUUID(self.portal.doc1)

        dm.set(f"../resolveuid/{doc_uuid}")
        self.assertEqual(serializer(), self.portal.doc1.absolute_url())

        # Support for variable interpolation is still present
        dm.set("${portal_url}/doc1")
        self.assertEqual(serializer(), self.portal.doc1.absolute_url())

        dm.set("/doc1")
        self.assertEqual(serializer(), "/doc1")

        dm.set("/doc2")
        self.assertEqual(serializer(), "/doc2")


class TestDexterityImageFieldSerializingOriginalAndPNGScales(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING
    maxDiff = None

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc1", title="Test Document"
            )
        ]

    def serialize(self, fieldname, value):
        for schema in iterSchemata(self.doc1):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        dm = getMultiAdapter((self.doc1, field), IDataManager)
        dm.set(value)
        serializer = getMultiAdapter((field, self.doc1, self.request), IFieldSerializer)
        return serializer()

    def test_namedimage_field_serialization_returns_dict_with_original_scale(self):
        """In Plone >= 5.2 the image returned when requesting an image
        scale with the same width and height of the original image is
        the actual original image in its original format"""
        image_file = os.path.join(os.path.dirname(__file__), "1024x768.gif")
        with open(image_file, "rb") as f:
            image_data = f.read()
        fn = "test_namedimage_field"
        scale_url_uuid = "uuid_1"
        with patch_scale_uuid(scale_url_uuid):
            value = self.serialize(
                fn,
                NamedImage(
                    data=image_data, contentType="image/gif", filename="1024x768.gif"
                ),
            )
            self.assertTrue(isinstance(value, dict), "Not a <dict>")

            obj_url = self.doc1.absolute_url()

            # Original image is still a "scale"
            # scaled images are converted to PNG in Plone = 5.2
            original_download_url = "{}/@@images/{}.{}".format(
                obj_url, scale_url_uuid, "gif"
            )

            scale_download_url = "{}/@@images/{}.{}".format(
                obj_url, scale_url_uuid, "png"
            )
            scales = {
                "listing": {
                    "download": scale_download_url,
                    "width": 16,
                    "height": 12,
                },
                "icon": {"download": scale_download_url, "width": 32, "height": 24},
                "tile": {"download": scale_download_url, "width": 64, "height": 48},
                "thumb": {
                    "download": scale_download_url,
                    "width": 128,
                    "height": 96,
                },
                "mini": {
                    "download": scale_download_url,
                    "width": 200,
                    "height": 150,
                },
                "preview": {
                    "download": scale_download_url,
                    "width": 400,
                    "height": 300,
                },
                "large": {
                    "download": scale_download_url,
                    "width": 768,
                    "height": 576,
                },
            }
            if HAS_PLONE_6:
                # PLIP #3279 amended the image scales
                # https://github.com/plone/Products.CMFPlone/pull/3450
                scales["great"] = {
                    "download": scale_download_url,
                    "height": 768,
                    "width": 1024,
                }
                scales["huge"] = {
                    "download": scale_download_url,
                    "height": 768,
                    "width": 1024,
                }
                scales["larger"] = {
                    "download": scale_download_url,
                    "height": 750,
                    "width": 1000,
                }
                scales["large"] = {
                    "download": scale_download_url,
                    "height": 600,
                    "width": 800,
                }
                scales["teaser"] = {
                    "download": scale_download_url,
                    "height": 450,
                    "width": 600,
                }
            self.assertEqual(
                {
                    "filename": "1024x768.gif",
                    "content-type": "image/gif",
                    "size": 1514,
                    "download": original_download_url,
                    "width": 1024,
                    "height": 768,
                    "scales": scales,
                },
                value,
            )

    def test_namedimage_field_serialization_doesnt_choke_on_corrupt_image(self):
        """In Plone >= 5.2 the original image file is not a "scale", so its url
        is returned as is and we need to check it, but the scales should be empty"""
        image_data = b"INVALID IMAGE DATA"
        fn = "test_namedimage_field"
        scale_url_uuid = "uuid_1"
        with patch_scale_uuid(scale_url_uuid):
            value = self.serialize(
                fn,
                NamedImage(
                    data=image_data, contentType="image/gif", filename="1024x768.gif"
                ),
            )

        obj_url = self.doc1.absolute_url()
        self.assertEqual(
            {
                "content-type": "image/gif",
                "download": "{}/@@images/{}.{}".format(obj_url, scale_url_uuid, "gif"),
                "filename": "1024x768.gif",
                "height": -1,
                "scales": {},
                "size": 18,
                "width": -1,
            },
            value,
        )

    def test_namedblobimage_field_serialization_returns_dict_with_original_scale(self):
        """In Plone >= 5.2 the image returned when requesting an image
        scale with the same width and height of the original image is
        the actual original image in its original format"""
        image_file = os.path.join(os.path.dirname(__file__), "1024x768.gif")
        with open(image_file, "rb") as f:
            image_data = f.read()
        fn = "test_namedblobimage_field"
        scale_url_uuid = "uuid_1"
        with patch_scale_uuid(scale_url_uuid):
            value = self.serialize(
                fn,
                NamedBlobImage(
                    data=image_data, contentType="image/gif", filename="1024x768.gif"
                ),
            )
            self.assertTrue(isinstance(value, dict), "Not a <dict>")

            obj_url = self.doc1.absolute_url()

            # Original image is still a "scale"
            # scaled images are converted to PNG in Plone = 5.2
            original_download_url = "{}/@@images/{}.{}".format(
                obj_url, scale_url_uuid, "gif"
            )

            scale_download_url = "{}/@@images/{}.{}".format(
                obj_url, scale_url_uuid, "png"
            )
            scales = {
                "listing": {
                    "download": scale_download_url,
                    "width": 16,
                    "height": 12,
                },
                "icon": {"download": scale_download_url, "width": 32, "height": 24},
                "tile": {"download": scale_download_url, "width": 64, "height": 48},
                "thumb": {
                    "download": scale_download_url,
                    "width": 128,
                    "height": 96,
                },
                "mini": {
                    "download": scale_download_url,
                    "width": 200,
                    "height": 150,
                },
                "preview": {
                    "download": scale_download_url,
                    "width": 400,
                    "height": 300,
                },
                "large": {
                    "download": scale_download_url,
                    "width": 768,
                    "height": 576,
                },
            }
            if HAS_PLONE_6:
                # PLIP #3279 amended the image scales
                # https://github.com/plone/Products.CMFPlone/pull/3450
                scales["great"] = {
                    "download": scale_download_url,
                    "height": 768,
                    "width": 1024,
                }
                scales["huge"] = {
                    "download": scale_download_url,
                    "height": 768,
                    "width": 1024,
                }
                scales["larger"] = {
                    "download": scale_download_url,
                    "height": 750,
                    "width": 1000,
                }
                scales["large"] = {
                    "download": scale_download_url,
                    "height": 600,
                    "width": 800,
                }
                scales["teaser"] = {
                    "download": scale_download_url,
                    "height": 450,
                    "width": 600,
                }
            self.assertEqual(
                {
                    "filename": "1024x768.gif",
                    "content-type": "image/gif",
                    "size": 1514,
                    "download": original_download_url,
                    "width": 1024,
                    "height": 768,
                    "scales": scales,
                },
                value,
            )

    def test_namedblobimage_field_serialization_doesnt_choke_on_corrupt_image(self):
        """In Plone >= 5.2 the original image file is not a "scale", so its url
        is returned as is and we need to check it, but the scales should be empty"""
        image_data = b"INVALID IMAGE DATA"
        fn = "test_namedblobimage_field"
        scale_url_uuid = "uuid_1"
        with patch_scale_uuid(scale_url_uuid):
            value = self.serialize(
                fn,
                NamedBlobImage(
                    data=image_data, contentType="image/gif", filename="1024x768.gif"
                ),
            )

        obj_url = self.doc1.absolute_url()
        self.assertEqual(
            {
                "content-type": "image/gif",
                "download": "{}/@@images/{}.{}".format(obj_url, scale_url_uuid, "gif"),
                "filename": "1024x768.gif",
                "height": -1,
                "scales": {},
                "size": 18,
                "width": -1,
            },
            value,
        )


class TestDexterityFieldSerializers(TestCase):
    def default_field_serializer(self):
        verifyClass(IFieldSerializer, DefaultFieldSerializer)
