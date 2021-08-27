from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityItem
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.tests.dxtypes import ITestAnnotationsBehavior
from plone.restapi.tests.mixin_ordering import OrderingMixin
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import provideHandler
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import json
import unittest


class TestDXContentDeserializer(unittest.TestCase, OrderingMixin):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.portal.invokeFactory(
            "DXTestDocument",
            id="doc1",
            test_textline_field="Test Document",
            test_readonly_field="readonly",
        )

        # ordering setup
        self.folder = self.portal[
            self.portal.invokeFactory("Folder", id="folder1", title="Test folder")
        ]

        for x in range(1, 10):
            self.folder.invokeFactory(
                "Document", id="doc" + str(x), title="Test doc " + str(x)
            )

    def deserialize(self, body="{}", validate_all=False, context=None, create=False):
        context = context or self.portal.doc1
        self.request["BODY"] = body
        deserializer = getMultiAdapter((context, self.request), IDeserializeFromJson)
        return deserializer(validate_all=validate_all, create=create)

    def test_deserializer_raises_with_invalid_body(self):
        with self.assertRaises(DeserializationError) as cm:
            self.deserialize(body="Not a JSON object")
        self.assertEqual("No JSON object could be decoded", cm.exception.msg)

    def test_deserializer_raises_with_malformed_body(self):
        with self.assertRaises(DeserializationError) as cm:
            self.deserialize(body="[1,2,3]")
        self.assertEqual("Malformed body", cm.exception.msg)

    def test_deserializer_updates_field_value(self):
        self.deserialize(body='{"test_textline_field": "My Item"}')
        self.assertEqual("My Item", self.portal.doc1.test_textline_field)

    def test_deserializer_ignores_readonly_fields(self):
        self.deserialize(body='{"test_readonly_field": "Foo"}')
        self.assertEqual("readonly", self.portal.doc1.test_readonly_field)

    def test_deserializer_notifies_object_modified(self):
        def handler(obj, event):
            obj._handler_called = True

        provideHandler(handler, (IDexterityItem, IObjectModifiedEvent))
        self.deserialize(body='{"test_textline_field": "My Item"}')
        self.assertTrue(
            getattr(self.portal.doc1, "_handler_called", False),
            "IObjectEditedEvent not notified",
        )

    def test_deserializer_modified_event_contains_descriptions(self):
        def handler(obj, event):
            self.event = event

        provideHandler(handler, (IDexterityItem, IObjectModifiedEvent))
        self.deserialize(body='{"test_textline_field": "My Item"}')
        self.assertEqual(1, len(self.event.descriptions))
        self.assertEqual(
            ("IDXTestDocumentSchema.test_textline_field",),
            self.event.descriptions[0].attributes,
        )

    def test_deserializer_notifies_when_field_is_set_to_null(self):
        def handler(obj, event):
            obj._handler_called = True
            self.event = event

        provideHandler(handler, (IDexterityItem, IObjectModifiedEvent))
        self.deserialize(body='{"test_textline_field": null}')
        self.assertTrue(
            getattr(self.portal.doc1, "_handler_called", False),
            "IObjectModifiedEvent not notified",
        )
        self.assertEqual(
            ("IDXTestDocumentSchema.test_textline_field",),
            self.event.descriptions[0].attributes,
        )

    def test_deserializer_does_not_update_field_without_write_permission(self):
        self.portal.doc1.test_write_permission_field = "Test Write Permission"
        setRoles(self.portal, TEST_USER_ID, ["Member", "Contributor", "Editor"])
        self.deserialize(body='{"test_write_permission_field": "Foo"}')
        self.assertEqual(
            "Test Write Permission", self.portal.doc1.test_write_permission_field
        )

    def test_deserializer_updates_field_with_write_permission(self):
        self.portal.doc1.test_write_permission_field = "Test Write Permission"
        setRoles(self.portal, TEST_USER_ID, ["Member", "Manager"])
        self.deserialize(body='{"test_write_permission_field": "Foo"}')
        self.assertEqual("Foo", self.portal.doc1.test_write_permission_field)

    def test_deserializer_validates_invariant(self):
        with self.assertRaises(BadRequest) as cm:
            self.deserialize(
                body='{"test_invariant_field1": "Foo",'
                ' "test_invariant_field2": "Bar"}'
            )
        self.assertEqual(
            "Must have same values", str(cm.exception.args[0][0]["message"])
        )

    def test_deserializer_updates_behavior_field_value(self):
        self.deserialize(body='{"test_behavior_field": "My Value"}')
        self.assertEqual("My Value", self.portal.doc1.test_behavior_field)

    def test_deserializer_updates_behavior_field_value_in_annotations(self):
        self.deserialize(body='{"test_annotations_behavior_field": "My Value"}')
        self.assertEqual(
            "My Value",
            ITestAnnotationsBehavior(self.portal.doc1).test_annotations_behavior_field,
        )

    def test_deserializer_raises_if_required_value_is_missing(self):
        # Value missing from request
        with self.assertRaises(BadRequest) as cm:
            self.deserialize(
                body='{"test_textline_field": "My Value"}', validate_all=True
            )
        self.assertEqual(
            "Required input is missing.", cm.exception.args[0][0]["message"]
        )

        # An empty string should be considered a missing value
        with self.assertRaises(BadRequest) as cm:
            self.deserialize(body='{"test_textline_field": ""}', validate_all=True)
        self.assertEqual(
            "Required input is missing.", cm.exception.args[0][0]["message"]
        )

    def test_deserializer_succeeds_if_required_value_is_provided(self):
        self.deserialize(body='{"test_required_field": "My Value"}', validate_all=True)
        self.assertEqual("My Value", self.portal.doc1.test_required_field)

    def test_deserializer_does_not_store_default_value(self):
        # XXX: Dexterity has an odd behavior with default values.
        # If a field's value is set to it's default value, it is not stored
        # because z3c.form only updates a field's value if the new value is
        # different from the previous one. Dexterity has a fallback to lookup
        # an attribute's value from the schema's default value if the attribute
        # doesn't exist. Thus the previous value is the default value and the
        # field doesn't get updated if the new value is also the default value.
        # Right now, we want to have the same behavior in the API for
        # consistency reasons.
        self.deserialize(body='{"test_default_value_field": "Default"}')
        self.assertNotIn(
            "test_default_value_field",
            dir(self.portal.doc1),
            "Default value unexpectedly stored.",
        )

    def test_deserializer_passes_validation_with_not_provided_defaults(self):
        self.deserialize(body='{"test_required_field": "My Value"}', validate_all=True)
        self.assertEqual("Default", self.portal.doc1.test_default_value_field)
        self.assertEqual("DefaultFactory", self.portal.doc1.test_default_factory_field)

    def test_deserializer_sets_missing_value_when_receiving_null(self):
        self.deserialize(body='{"test_missing_value_field": null}')
        self.assertEqual("missing", self.portal.doc1.test_missing_value_field)

    def test_deserializer_sets_missing_value_on_required_field(self):
        """We don't set missing_value if the field is required"""
        self.deserialize(body='{"test_missing_value_required_field": "valid value"}')
        with self.assertRaises(BadRequest) as cm:
            self.deserialize(body='{"test_missing_value_required_field": null}')
        self.assertEqual(
            "valid value", self.portal.doc1.test_missing_value_required_field
        )
        self.assertEqual(
            (
                "test_missing_value_required_field is a required field.",
                "Setting it to null is not allowed.",
            ),
            cm.exception.args[0][0]["message"],
        )
        self.assertEqual(
            "test_missing_value_required_field", cm.exception.args[0][0]["field"]
        )

    def test_set_layout(self):
        current_layout = self.portal.doc1.getLayout()
        self.assertNotEqual(current_layout, "my_new_layout")
        self.deserialize(body='{"layout": "my_new_layout"}')
        self.assertEqual("my_new_layout", self.portal.doc1.getLayout())

    def test_deserializer_should_store_default_value_on_content_creation(self):
        # Store default_factory values during content creation. This is specially
        # important for content types like Event, where the default_factory returns
        # a distinct value each time.
        self.portal.invokeFactory(
            "DXTestDocument",
            id="doc_default_value",
        )
        context = self.portal.doc_default_value
        default_value = "DefaultFactory"
        body = {"test_default_factory_field": default_value}
        self.deserialize(body=json.dumps(body), context=context, create=True)
        self.assertIn(
            "test_default_factory_field",
            dir(context),
            "Default value still available.",
        )


class TestDXContentSerializerDeserializer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.portal.invokeFactory(
            "DXTestDocument",
            id="doc1",
            test_textline_field="Test Document",
            test_readonly_field="readonly",
        )

        self.portal.invokeFactory(
            "DXTestDocument",
            id="doc2",
            test_textline_field="Test Document 2",
            test_readonly_field="readonly",
        )

    def deserialize(self, field, value, validate_all=False, context=None):
        context = context or self.portal.doc1
        body = {}
        body[field] = value
        body = json.dumps(body)
        self.request["BODY"] = body
        deserializer = getMultiAdapter((context, self.request), IDeserializeFromJson)
        return deserializer(validate_all=validate_all)

    def serialize(self, field):
        serializer = getMultiAdapter((self.portal.doc1, self.request), ISerializeToJson)
        return serializer()[field]

    def test_serialize2deserialize_relation(self):
        value = str(self.portal.doc2.UID())
        self.deserialize("test_relationchoice_field", value)

        serialization_value = self.serialize("test_relationchoice_field")

        self.deserialize("test_relationchoice_field", serialization_value)

        self.assertEqual(
            serialization_value["@id"],
            self.portal.doc1.test_relationchoice_field.to_object.absolute_url(),
        )
