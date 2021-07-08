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
from plone.restapi.tests.dxtypes import IDXTestDocumentSchema
from pytz import timezone
from zope.component import getMultiAdapter
from zope.schema import Field
from zope.schema._bootstrapinterfaces import RequiredMissing
from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.interfaces import ValidationError

import unittest


class RequiredField:
    """Context manager that will make a field required and back to old state."""

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
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.portal.invokeFactory("DXTestDocument", id="doc1", title="Test Document")

    def deserialize(self, fieldname, value):
        for schema in iterSchemata(self.portal.doc1):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        deserializer = getMultiAdapter(
            (field, self.portal.doc1, self.request), IFieldDeserializer
        )
        return deserializer(value)

    def test_ascii_deserialization_returns_native_string(self):
        value = self.deserialize("test_ascii_field", "Foo")
        self.assertTrue(isinstance(value, str), "Not a <str>")
        self.assertEqual("Foo", value)

    def test_asciiline_deserialization_returns_native_string(self):
        value = self.deserialize("test_asciiline_field", "Foo")
        self.assertTrue(isinstance(value, str), "Not a <str>")
        self.assertEqual("Foo", value)

    def test_bool_deserialization_returns_true(self):
        value = self.deserialize("test_bool_field", True)
        self.assertTrue(isinstance(value, bool), "Not a <bool>")
        self.assertEqual(True, value)

    def test_bool_deserialization_returns_false(self):
        value = self.deserialize("test_bool_field", False)
        self.assertTrue(isinstance(value, bool), "Not a <bool>")
        self.assertEqual(False, value)

    def test_bytes_deserialization_returns_bytestring(self):
        value = self.deserialize("test_bytes_field", "Foo")
        self.assertTrue(isinstance(value, bytes), "Not a <bytes>")
        self.assertEqual(b"Foo", value)

    def test_bytesline_deserialization_returns_bytestring(self):
        value = self.deserialize("test_bytesline_field", "Foo")
        self.assertTrue(isinstance(value, bytes), "Not a <bytes>")
        self.assertEqual(b"Foo", value)

    def test_choice_deserialization_returns_vocabulary_item(self):
        value = self.deserialize("test_choice_field", "bar")
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("bar", value)

    def test_choice_deserialization_from_token_returns_vocabulary_value(self):
        value = self.deserialize("test_choice_field_with_vocabulary", "token1")
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("value1", value)

    def test_choice_deserialization_from_value_returns_vocabulary_value(self):
        value = self.deserialize("test_choice_field_with_vocabulary", "value1")
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("value1", value)

    def test_choice_deserialization_from_term_returns_vocabulary_value(self):
        value = self.deserialize(
            "test_choice_field_with_vocabulary",
            {"token": "token1", "title": "title1"},
        )
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("value1", value)

    def test_date_deserialization_returns_date(self):
        value = self.deserialize("test_date_field", "2015-12-20")
        self.assertTrue(isinstance(value, date))
        self.assertEqual(date(2015, 12, 20), value)

    def test_datetime_deserialization_returns_datetime(self):
        value = self.deserialize("test_datetime_field", "2015-12-20T10:39:54.361Z")
        self.assertTrue(isinstance(value, datetime), "Not a <datetime>")
        self.assertEqual(datetime(2015, 12, 20, 10, 39, 54, 361000), value)

    def test_datetime_deserialization_handles_timezone(self):
        value = self.deserialize("test_datetime_field", "2015-12-20T10:39:54.361+01")
        self.assertEqual(datetime(2015, 12, 20, 9, 39, 54, 361000), value)

    def test_datetime_with_tz_deserialization_keeps_timezone(self):
        value = self.deserialize("test_datetime_tz_field", "2015-12-20T10:39:54.361+01")
        self.assertEqual(
            timezone("Europe/Zurich").localize(
                datetime(2015, 12, 20, 10, 39, 54, 361000)
            ),
            value,
        )

    def test_datetime_with_tz_deserialization_converts_timezone(self):
        value = self.deserialize("test_datetime_tz_field", "2015-12-20T10:39:54.361-04")
        self.assertEqual(
            timezone("Europe/Zurich").localize(
                datetime(2015, 12, 20, 15, 39, 54, 361000)
            ),
            value,
        )

    def test_datetime_with_tz_deserialization_adds_timezone(self):
        value = self.deserialize("test_datetime_tz_field", "2015-12-20T10:39:54.361")
        self.assertEqual(
            timezone("Europe/Zurich").localize(
                datetime(2015, 12, 20, 11, 39, 54, 361000)
            ),
            value,
        )

    def test_datetime_with_tz_deserialization_handles_dst(self):
        value = self.deserialize("test_datetime_tz_field", "2015-05-20T10:39:54.361+02")
        self.assertEqual(
            timezone("Europe/Zurich").localize(
                datetime(2015, 5, 20, 10, 39, 54, 361000)
            ),
            value,
        )

    def test_datetime_deserialization_none(self):
        # Make sure we don't construct a datetime out of nothing
        value = self.deserialize("test_datetime_field", None)
        self.assertEqual(value, None)

    def test_datetime_deserialization_required(self):
        field_name = "test_datetime_field"
        field = IDXTestDocumentSchema.get(field_name)
        with RequiredField(field):
            with self.assertRaises(RequiredMissing):
                self.deserialize(field_name, None)

    def test_text_deserialization_returns_decimal(self):
        value = self.deserialize("test_decimal_field", "1.1")
        self.assertTrue(isinstance(value, Decimal), "Not a <Decimal>")
        self.assertEqual(Decimal("1.1"), value)

    def test_dict_deserialization_returns_dict(self):
        value = self.deserialize("test_dict_field", {"key": "value"})
        self.assertTrue(isinstance(value, dict), "Not a <dict>")
        self.assertEqual({"key": "value"}, value)

    def test_float_deserialization_returns_float(self):
        value = self.deserialize("test_float_field", 1.0)
        self.assertTrue(isinstance(value, float), "Not a <float>")
        self.assertEqual(1.0, value)

    def test_frozenset_deserialization_returns_frozenset(self):
        value = self.deserialize("test_frozenset_field", ["foo", "bar"])
        self.assertTrue(isinstance(value, frozenset), "Not a <frozenset>")
        self.assertEqual(frozenset(["foo", "bar"]), value)

    def test_int_deserialization_returns_int(self):
        value = self.deserialize("test_int_field", 22)
        self.assertTrue(isinstance(value, int), "Not an <int>")
        self.assertEqual(22, value)

    def test_list_deserialization_returns_list(self):
        value = self.deserialize("test_list_field", [1, 2, 3])
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual([1, 2, 3], value)

    def test_list_deserialization_from_tokens_returns_list_of_values(self):
        value = self.deserialize(
            "test_list_field_with_choice_with_vocabulary", ["token1", "token3"]
        )
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual(["value1", "value3"], value)

    def test_list_deserialization_from_values_returns_list_of_values(self):
        value = self.deserialize(
            "test_list_field_with_choice_with_vocabulary", ["value1", "value3"]
        )
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual(["value1", "value3"], value)

    def test_list_deserialization_from_terms_returns_list_of_values(self):
        value = self.deserialize(
            "test_list_field_with_choice_with_vocabulary",
            [
                {"token": "token1", "title": "title1"},
                {"token": "token3", "title": "title3"},
            ],
        )
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual(["value1", "value3"], value)

    def test_set_deserialization_returns_set(self):
        value = self.deserialize("test_set_field", [1, 2, 3])
        self.assertTrue(isinstance(value, set), "Not a <set>")
        self.assertEqual({1, 2, 3}, value)

    def test_text_deserialization_returns_unicode(self):
        value = self.deserialize("test_text_field", "Foo")
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("Foo", value)

    def test_textline_deserialization_returns_unicode(self):
        value = self.deserialize("test_textline_field", "Foo")
        self.assertTrue(isinstance(value, str), "Not an <unicode>")
        self.assertEqual("Foo", value)

    def test_time_deserialization_returns_time(self):
        value = self.deserialize("test_time_field", "10:39:54.361Z")
        self.assertTrue(isinstance(value, time), "Not a <time>")
        self.assertEqual(time(10, 39, 54, 361000), value)

    def test_timedelta_deserialization_returns_timedela(self):
        value = self.deserialize("test_timedelta_field", 3600.0)
        self.assertTrue(isinstance(value, timedelta), "Not a <timedelta>")
        self.assertEqual(timedelta(seconds=3600), value)

    def test_tuple_deserialization_returns_tuple(self):
        value = self.deserialize("test_tuple_field", [1, 2, 3])
        self.assertTrue(isinstance(value, tuple), "Not a <tuple>")
        self.assertEqual((1, 2, 3), value)

    def test_nested_list_deserialization_returns_nested_list(self):
        value = self.deserialize("test_nested_list_field", [[1, "foo"], [2, "bar"]])
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertTrue(isinstance(value[0], tuple), "Not a <tuple>")
        self.assertTrue(isinstance(value[1], tuple), "Not a <tuple>")

    def test_nested_dict_deserialization_returns_nested_dict(self):
        value = self.deserialize(
            "test_nested_dict_field", {"1": ["foo", "bar"], "2": ["spam", "eggs"]}
        )
        self.assertTrue(isinstance(value, dict), "Not a <dict>")
        self.assertIn("1", value)
        self.assertTrue(isinstance(value["1"], tuple), "Not a <tuple>")
        self.assertIn("2", value)
        self.assertTrue(isinstance(value["2"], tuple), "Not a <tuple>")

    def test_richtext_deserialization_from_unicode_returns_richtext(self):
        value = self.deserialize("test_richtext_field", "<p>a paragraph</p>")
        self.assertTrue(isinstance(value, RichTextValue), "Not a <RichTextValue>")
        self.assertEqual("<p>a paragraph</p>", value.raw)

    def test_richtext_deserialization_from_dict_returns_richtext(self):
        value = self.deserialize("test_richtext_field", {"data": "Some text"})
        self.assertTrue(isinstance(value, RichTextValue), "Not a <RichTextValue>")
        self.assertEqual("Some text", value.raw)

    def test_richtext_deserialization_sets_mime_type(self):
        value = self.deserialize(
            "test_richtext_field",
            {"data": "Some text", "content-type": "text/plain"},
        )
        self.assertEqual("text/plain", value.mimeType)

    def test_richtext_deserialization_sets_encoding(self):
        value = self.deserialize(
            "test_richtext_field", {"data": "Some text", "encoding": "latin1"}
        )
        self.assertEqual("latin1", value.encoding)

    def test_richtext_deserialization_fix_apostrophe(self):
        value = self.deserialize("test_richtext_field", "<p>char with &#x27;</p>")
        self.assertEqual("<p>char with '</p>", value.raw)

    def test_namedfield_deserialization_decodes_value(self):
        value = self.deserialize(
            "test_namedfile_field",
            {"data": "U3BhbSBhbmQgZWdncyE=", "encoding": "base64"},
        )
        self.assertEqual(b"Spam and eggs!", value.data)

    def test_namedfield_deserialization_sets_content_type(self):
        value = self.deserialize(
            "test_namedfile_field",
            {"data": "Spam and eggs!", "content-type": "text/plain"},
        )
        self.assertEqual("text/plain", value.contentType)

    def test_namedfield_deserialization_sets_filename(self):
        value = self.deserialize(
            "test_namedfile_field",
            {"data": "Spam and eggs!", "filename": "doc.txt"},
        )
        self.assertEqual("doc.txt", value.filename)

    def test_namedfile_deserialization_returns_namedfile(self):
        value = self.deserialize("test_namedfile_field", {"data": "Spam and eggs!"})
        self.assertTrue(isinstance(value, namedfile.NamedFile), "Not a <NamedFile>")
        self.assertEqual(b"Spam and eggs!", value.data)

    def test_namedimage_deserialization_returns_namedimage(self):
        value = self.deserialize(
            "test_namedimage_field",
            {
                "data": "R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=",
                "encoding": "base64",
                "content-type": "image/gif",
            },
        )
        self.assertTrue(isinstance(value, namedfile.NamedImage), "Not a <NamedImage>")
        self.assertTrue(value.data.startswith(b"GIF89a"))

    def test_namedblobfile_deserialization_returns_namedblobfile(self):
        value = self.deserialize("test_namedblobfile_field", {"data": "Spam and eggs!"})
        self.assertTrue(
            isinstance(value, namedfile.NamedBlobFile), "Not a <NamedBlobFile>"
        )
        self.assertEqual(b"Spam and eggs!", value.data)

    def test_namedblobimage_deserialization_returns_namedblobimage(self):
        value = self.deserialize(
            "test_namedblobimage_field",
            {
                "data": "R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=",
                "encoding": "base64",
                "content-type": "image/gif",
            },
        )
        self.assertTrue(
            isinstance(value, namedfile.NamedBlobImage), "Not a <NamedBlobImage>"
        )
        self.assertTrue(value.data.startswith(b"GIF89a"))

    def test_namedblobimage_deserialization_fed_with_null_removes_image(self):
        # null in json translates to None in python.
        value = self.deserialize("test_namedblobimage_field", None)
        self.assertFalse(value)

    def test_namedblobfile_deserialization_fed_with_null_removes_file(self):
        # null in json translates to None in python.
        value = self.deserialize("test_namedblobfile_field", None)
        self.assertFalse(value)

    def test_namedblobfile_deserialize_required(self):
        field_name = "test_namedblobfile_field"
        field = IDXTestDocumentSchema.get(field_name)
        with RequiredField(field):
            with self.assertRaises(RequiredMissing):
                self.deserialize(field_name, None)

    def test_namedblobimage_deserialize_required(self):
        field_name = "test_namedblobimage_field"
        field = IDXTestDocumentSchema.get(field_name)
        with RequiredField(field):
            with self.assertRaises(RequiredMissing):
                self.deserialize(field_name, None)

    def test_relationchoice_deserialization_from_uid_returns_document(self):
        doc2 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc2", title="Referenceable Document"
            )
        ]
        value = self.deserialize("test_relationchoice_field", str(doc2.UID()))
        self.assertEqual(doc2, value)

    def test_relationchoice_deserialization_from_url_returns_document(self):
        doc2 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc2", title="Referenceable Document"
            )
        ]
        value = self.deserialize("test_relationchoice_field", str(doc2.absolute_url()))
        self.assertEqual(doc2, value)

    def test_relationchoice_deserialization_from_path_returns_document(self):
        doc2 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc2", title="Referenceable Document"
            )
        ]
        value = self.deserialize("test_relationchoice_field", "/doc2")
        self.assertEqual(doc2, value)

    def test_relationchoice_deserialization_from_invalid_intid_raises(self):
        with self.assertRaises(ValueError) as cm:
            self.deserialize("test_relationchoice_field", 123456789)
        self.assertEqual(
            str(cm.exception), "Could not resolve object for intid=123456789"
        )
        self.assertEqual(400, self.request.response.getStatus())

    def test_relationchoice_deserialization_from_invalid_uid_raises(self):
        with self.assertRaises(ValueError) as cm:
            self.deserialize(
                "test_relationchoice_field",
                "ac12b24913cf45c6863937367aacc263",
            )
        self.assertEqual(
            str(cm.exception),
            "Could not resolve object for UID=ac12b24913cf45c6863937367aacc263",
        )
        self.assertEqual(400, self.request.response.getStatus())

    def test_relationchoice_deserialization_from_invalid_url_raises(self):
        with self.assertRaises(ValueError) as cm:
            self.deserialize(
                "test_relationchoice_field",
                "http://nohost/plone/doesnotexist",
            )
        self.assertEqual(
            str(cm.exception),
            "Could not resolve object for URL=http://nohost/plone/doesnotexist",
        )
        self.assertEqual(400, self.request.response.getStatus())

    def test_relationchoice_deserialization_from_invalid_path_raises(self):
        with self.assertRaises(ValueError) as cm:
            self.deserialize("test_relationchoice_field", "/doesnotexist")
        self.assertEqual(
            str(cm.exception), "Could not resolve object for path=/doesnotexist"
        )
        self.assertEqual(400, self.request.response.getStatus())

    def test_relationlist_deserialization_returns_list_of_documents(self):
        doc2 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc2", title="Referenceable Document"
            )
        ]
        doc3 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc3", title="Referenceable Document"
            )
        ]
        value = self.deserialize(
            "test_relationlist_field",
            [str(doc2.UID()), str(doc3.UID())],
        )
        self.assertTrue(isinstance(value, list), "Not a <list>")
        self.assertEqual(doc2, value[0])
        self.assertEqual(doc3, value[1])

    def test_default_deserializer_validates_value(self):
        with self.assertRaises(ValidationError):
            self.deserialize("test_maxlength_field", "01234567890")

    def test_datetime_deserializer_handles_invalid_value(self):
        with self.assertRaises(ValueError) as cm:
            self.deserialize("test_datetime_field", "2015-15-15T10:39:54.361Z")
        self.assertEqual("Invalid date: 2015-15-15T10:39:54.361Z", str(cm.exception))

    def test_datetime_deserializer_validates_value(self):
        with self.assertRaises(ValidationError):
            self.deserialize("test_datetime_min_field", "1999-12-20T10:39:54.361Z")

    def test_collection_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize("test_list_value_type_field", [1, b"2", 3])

        # This validation error is actually produced by the
        # DefaultFieldDeserializer that the CollectionFieldDeserializer will
        # delegate to for deserializing collection items.
        self.assertEqual("Object is of wrong type.", cm.exception.doc())
        self.assertEqual((b"2", (int,), ""), cm.exception.args)

    def test_dict_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize("test_dict_key_type_field", {"k": "v"})

        # This validation error is actually produced by the
        # DefaultFieldDeserializer that the DictFieldSerializer will delegate
        # to for deserializing keys and values.
        # We check for two sets of exception details
        # because zope.schema changed its exception...
        self.assertIn(
            cm.exception.doc(), ("Object is of wrong type.", "Invalid int literal.")
        )
        self.assertIn(
            cm.exception.args,
            (
                ("k", (int,), ""),
                ("invalid literal for int() with base 10: 'k'",),
            ),
        )

    def test_time_deserializer_handles_invalid_value(self):
        with self.assertRaises(ValueError) as cm:
            self.deserialize("test_time_field", "midnight")
        self.assertEqual("Invalid time: midnight", str(cm.exception))

    def test_time_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize("test_time_min_field", "00:39:54.361Z")
        self.assertEqual("Value is too small", cm.exception.doc())

    def test_timedelta_deserializer_handles_invalid_value(self):
        with self.assertRaises(ValueError) as cm:
            self.deserialize("test_timedelta_field", "2h")
        self.assertIn(
            "unsupported type for timedelta seconds component:", str(cm.exception)
        )

    def test_timedelta_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize("test_timedelta_min_field", 50)
        self.assertEqual("Value is too small", cm.exception.doc())

    def test_namedfield_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize(
                "test_namedimage_field",
                {"data": "Spam and eggs!", "content-type": "text/plain"},
            )
        self.assertEqual("Invalid image file", cm.exception.doc())

    def test_namedfield_deserializer_download(self):
        # Handle when we post back the GET results.
        # This then has a 'download' key, and not a 'data' key.

        self.deserialize(
            "test_namedfile_field",
            {"download": "some download link", "content-type": "text/plain"},
        )

    def test_richtextfield_deserializer_validates_value(self):
        with self.assertRaises(ValidationError) as cm:
            self.deserialize(
                "test_richtext_field",
                {"data": "Spam and eggs!", "content-type": "text/xml"},
            )
        self.assertEqual("Object is of wrong type.", cm.exception.doc())

    def test_relationchoicefield_deserializer_validates_value(self):
        self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc3", title="Referenceable Document"
            )
        ]
        with self.assertRaises(ValidationError) as cm:
            self.deserialize("test_relationchoice_field", "/doc3")
        self.assertEqual("Constraint not satisfied", cm.exception.doc())

    def test_deserialize_with_context_bound_vocabulary(self):
        value = self.deserialize(
            "test_list_choice_with_context_vocabulary_field", ["portal_catalog"]
        )
        self.assertEqual(["portal_catalog"], value)

    def test_textline_deserializer_strips_value(self):
        value = self.deserialize("test_textline_field", "  aa  ")
        self.assertEqual(value, "aa")

    def test_default_field_deserializer_validates_value(self):
        class CustomIntField(Field):
            def constraint(self, value):
                if not isinstance(value, int):
                    raise ConstraintNotSatisfied
                return True

        field = CustomIntField()
        deserializer = getMultiAdapter(
            (field, self.portal.doc1, self.request), IFieldDeserializer
        )

        with self.assertRaises(ConstraintNotSatisfied):
            deserializer(b"not an int")

        self.assertEqual(42, deserializer(42))

    def test_textline_deserializer_for_links_convert_internal_links(self):
        self.portal.invokeFactory("Link", id="link", title="Test Link")
        link = self.portal.link
        field = None
        for schema in iterSchemata(link):
            if "remoteUrl" in schema:
                field = schema.get("remoteUrl")
                break
        deserializer = getMultiAdapter((field, link, self.request), IFieldDeserializer)

        self.assertEqual(
            "http://www.plone.com", deserializer(value="http://www.plone.com")
        )
        self.assertEqual(
            "${portal_url}/doc1", deserializer(value="http://nohost/plone/doc1")
        )

        # for other contents/fields does nothing
        value = self.deserialize("test_textline_field", "http://www.plone.com")
        self.assertEqual("http://www.plone.com", value)
        value = self.deserialize("test_textline_field", "http://nohost/plone/doc1")
        self.assertEqual(self.portal.doc1.absolute_url(), value)
