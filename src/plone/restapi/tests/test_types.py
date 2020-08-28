# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal
from plone.app.textfield import RichText
from plone.autoform import directives as form
from plone.dexterity.fti import DexterityFTI
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_for_fti
from plone.restapi.types.utils import get_jsonschema_for_portal_type
from plone.restapi.types.utils import get_jsonschema_properties
from plone.schema import Email
from plone.supermodel import model
from Products.CMFCore.utils import getToolByName
from unittest import TestCase
from z3c.form.browser.text import TextWidget
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class IDummySchema(model.Schema):

    field1 = schema.Bool(title=u"Foo", description=u"")

    field2 = schema.TextLine(title=u"Bar", description=u"")


class ITaggedValuesSchema(model.Schema):

    form.mode(field_mode_hidden="hidden")
    field_mode_hidden = schema.TextLine(title=u"ModeHidden", description=u"")

    form.mode(field_mode_display="display")
    field_mode_display = schema.TextLine(title=u"ModeDisplay", description=u"")

    form.mode(field_mode_input="input")
    field_mode_input = schema.TextLine(title=u"ModeInput", description=u"")

    field_mode_default = schema.TextLine(title=u"ModeInput", description=u"")

    parametrized_widget_field = schema.TextLine(title=u"Parametrized widget field")
    form.widget(
        "parametrized_widget_field", a_param="some_value", defaultFactory=lambda: "Foo"
    )

    not_parametrized_widget_field = schema.TextLine(
        title=u"No parametrized widget field"
    )
    form.widget(not_parametrized_widget_field=TextWidget)


class TestJsonSchemaUtils(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_get_jsonschema_properties(self):
        fieldsets = get_fieldsets(self.portal, self.request, IDummySchema)
        info = get_jsonschema_properties(self.portal, self.request, fieldsets)
        expected = {
            "field1": {
                "title": u"Foo",
                "description": u"",
                "factory": "Yes/No",
                "type": "boolean",
            },
            "field2": {
                "title": u"Bar",
                "description": u"",
                "factory": "Text line (String)",
                "type": "string",
            },
        }
        self.assertEqual(info, expected)

    def test_get_jsonschema_for_fti(self):
        portal = self.portal
        request = self.request
        ttool = getToolByName(portal, "portal_types")
        jsonschema = get_jsonschema_for_fti(ttool["Document"], portal, request)
        self.assertEqual(jsonschema["title"], "Page")
        self.assertEqual(jsonschema["type"], "object")
        self.assertIn("title", list(jsonschema["properties"]))
        self.assertIn("title", jsonschema["required"])
        self.assertEqual("default", jsonschema["fieldsets"][0]["id"])
        self.assertIn("title", jsonschema["fieldsets"][0]["fields"])
        self.assertIn("layouts", jsonschema)

        jsonschema = get_jsonschema_for_fti(
            ttool["Document"], portal, request, excluded_fields=["title"]
        )
        self.assertNotIn("title", list(jsonschema["properties"]))

    def test_get_jsonschema_for_fti_non_dx(self):
        """Make sure FTIs without lookupSchema are supported."""
        fti = self.portal.portal_types["Discussion Item"]
        self.assertFalse(hasattr(fti, "lookupSchema"))

        # This shouldn't raise an error.
        get_jsonschema_for_fti(fti, self.portal, self.request)

    def test_get_jsonschema_for_portal_type(self):
        portal = self.portal
        request = self.request
        jsonschema = get_jsonschema_for_portal_type("Document", portal, request)
        self.assertEqual(jsonschema["title"], "Page")
        self.assertEqual(jsonschema["type"], "object")
        self.assertIn("title", list(jsonschema["properties"]))
        self.assertIn("title", jsonschema["required"])
        self.assertEqual("default", jsonschema["fieldsets"][0]["id"])
        self.assertIn("title", jsonschema["fieldsets"][0]["fields"])

        jsonschema = get_jsonschema_for_portal_type(
            "Document", portal, request, excluded_fields=["title"]
        )
        self.assertNotIn("title", list(jsonschema["properties"]))


class TestTaggedValuesJsonSchemaUtils(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        fti = DexterityFTI("TaggedDocument")
        self.portal.portal_types._setObject("TaggedDocument", fti)
        fti.klass = "plone.dexterity.content.Container"
        fti.schema = "plone.restapi.tests.test_types.ITaggedValuesSchema"

    def test_get_jsonschema_with_hidden_field(self):
        ttool = getToolByName(self.portal, "portal_types")
        jsonschema = get_jsonschema_for_fti(
            ttool["TaggedDocument"], self.portal, self.request
        )

        self.assertEqual(
            "hidden", jsonschema["properties"]["field_mode_hidden"]["mode"]
        )
        self.assertEqual(
            "display", jsonschema["properties"]["field_mode_display"]["mode"]
        )
        self.assertEqual("input", jsonschema["properties"]["field_mode_input"]["mode"])

    def test_get_jsonschema_with_widget_params(self):
        ttool = getToolByName(self.portal, "portal_types")
        jsonschema = get_jsonschema_for_fti(
            ttool["TaggedDocument"], self.portal, self.request
        )
        self.assertEqual(
            "some_value",
            jsonschema["properties"]["parametrized_widget_field"]["widgetOptions"][
                "a_param"
            ],
        )

    def test_do_not_fail_with_non_parametrized_widget(self):
        ttool = getToolByName(self.portal, "portal_types")
        jsonschema = get_jsonschema_for_fti(
            ttool["TaggedDocument"], self.portal, self.request
        )
        self.assertEqual(
            u"No parametrized widget field",
            jsonschema["properties"]["not_parametrized_widget_field"]["title"],
        )

    def test_resolve_callable_widget_params(self):
        ttool = getToolByName(self.portal, "portal_types")
        jsonschema = get_jsonschema_for_fti(
            ttool["TaggedDocument"], self.portal, self.request
        )

        self.assertEqual(
            u"Foo",
            jsonschema["properties"]["parametrized_widget_field"]["widgetOptions"].get(
                "defaultFactory"
            ),
        )


class TestJsonSchemaProviders(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.dummy_vocabulary = SimpleVocabulary(
            [
                SimpleTerm(value=u"foo", title=u"Foo"),
                SimpleTerm(value=u"bar", title=u"Bar"),
            ]
        )

    from zope.interface import provider
    from zope.schema.interfaces import IContextSourceBinder

    @provider(IContextSourceBinder)
    def dummy_source_vocab(self, context):
        return SimpleVocabulary(
            [
                SimpleTerm(value=u"foo", title=u"Foo"),
                SimpleTerm(value=u"bar", title=u"Bar"),
            ]
        )

    def test_context_aware_default_factory(self):
        folder = self.portal[
            self.portal.invokeFactory("Folder", id="folder", title="My Folder")
        ]

        @provider(IContextAwareDefaultFactory)
        def uppercased_title_default(context):
            return context.title.upper()

        field = schema.TextLine(
            title=u"My field",
            description=u"My great field",
            defaultFactory=uppercased_title_default,
        )
        adapter = getMultiAdapter((field, folder, self.request), IJsonSchemaProvider)

        self.assertEqual(
            {
                "type": "string",
                "title": u"My field",
                "factory": u"Text line (String)",
                "description": u"My great field",
                "default": u"MY FOLDER",
            },
            adapter.get_schema(),
        )

    def test_textline(self):
        field = schema.TextLine(
            title=u"My field", description=u"My great field", default=u"foobar"
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": u"My field",
                "factory": u"Text line (String)",
                "description": u"My great field",
                "default": u"foobar",
            },
            adapter.get_schema(),
        )

    def test_text(self):
        field = schema.Text(
            title=u"My field",
            description=u"My great field",
            default=u"Lorem ipsum dolor sit amet",
            min_length=10,
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": u"My field",
                "description": u"My great field",
                "factory": u"Text",
                "widget": "textarea",
                "default": u"Lorem ipsum dolor sit amet",
                "minLength": 10,
            },
            adapter.get_schema(),
        )

    def test_bool(self):
        field = schema.Bool(
            title=u"My field", description=u"My great field", default=False
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "boolean",
                "title": u"My field",
                "description": u"My great field",
                "factory": u"Yes/No",
                "default": False,
            },
            adapter.get_schema(),
        )

    def test_float(self):
        field = schema.Float(
            title=u"My field",
            description=u"My great field",
            min=0.0,
            max=1.0,
            default=0.5,
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "minimum": 0.0,
                "maximum": 1.0,
                "type": "number",
                "title": u"My field",
                "description": u"My great field",
                "factory": u"Floating-point number",
                "default": 0.5,
            },
            adapter.get_schema(),
        )

    def test_email(self):
        field = Email(
            title=u"Email",
            description=u"Email field",
            default="foo@bar.com",
            min_length=10,
            max_length=20,
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": "Email",
                "description": "Email field",
                "factory": "Email",
                "widget": "email",
                "default": "foo@bar.com",
                "minLength": 10,
                "maxLength": 20,
            },
            adapter.get_schema(),
        )

    def test_password(self):
        field = schema.Password(
            title=u"Password",
            description=u"Password field",
            default=u"secret",
            min_length=4,
            max_length=8,
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": "Password",
                "description": "Password field",
                "factory": "Password",
                "widget": "password",
                "default": "secret",
                "minLength": 4,
                "maxLength": 8,
            },
            adapter.get_schema(),
        )

    def test_uri(self):
        field = schema.URI(
            title=u"URI",
            description=u"URI field",
            default="http://foo.bar",
            min_length=10,
            max_length=100,
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": "URI",
                "description": "URI field",
                "factory": "URL",
                "widget": "url",
                "default": "http://foo.bar",
                "minLength": 10,
                "maxLength": 100,
            },
            adapter.get_schema(),
        )

    def test_decimal(self):
        field = schema.Decimal(
            title=u"My field",
            description=u"My great field",
            min=Decimal(0),
            max=Decimal(1),
            default=Decimal(0.5),
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "minimum": 0.0,
                "maximum": 1.0,
                "type": "number",
                "factory": "Floating-point number",
                "title": u"My field",
                "description": u"My great field",
                "default": 0.5,
            },
            adapter.get_schema(),
        )

    def test_int(self):
        field = schema.Int(
            title=u"My field", description=u"My great field", min=0, max=100, default=50
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "minimum": 0,
                "maximum": 100,
                "type": "integer",
                "title": "My field",
                "description": "My great field",
                "factory": "Integer",
                "default": 50,
            },
            adapter.get_schema(),
        )

    def test_choice(self):
        field = schema.Choice(
            __name__="myfield",
            title=u"My field",
            description=u"My great field",
            vocabulary=self.dummy_vocabulary,
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": u"My field",
                "description": u"My great field",
                "factory": "Choice",
                "enum": ["foo", "bar"],
                "enumNames": ["Foo", "Bar"],
                "choices": [("foo", "Foo"), ("bar", "Bar")],
                "vocabulary": {"@id": "http://nohost/plone/@sources/myfield"},
            },
            adapter.get_schema(),
        )

    def test_choice_inline_array(self):
        field = schema.Choice(
            __name__="myfield",
            title=u"My field",
            description=u"My great field",
            values=["foo", "bar"],
        )

        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": u"My field",
                "description": u"My great field",
                "factory": "Choice",
                "enum": ["foo", "bar"],
                "enumNames": [None, None],
                "choices": [("foo", None), ("bar", None)],
                "vocabulary": {"@id": "http://nohost/plone/@sources/myfield"},
            },
            adapter.get_schema(),
        )

    def test_choice_named_vocab(self):
        field = schema.Choice(
            title=u"My field",
            description=u"My great field",
            vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes",
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": u"My field",
                "description": u"My great field",
                "factory": "Choice",
                "vocabulary": {
                    "@id": u"http://nohost/plone/@vocabularies/plone.app.vocabularies.ReallyUserFriendlyTypes"
                },  # noqa
            },
            adapter.get_schema(),
        )

    def test_choice_source_vocab(self):
        field = schema.Choice(
            __name__="myfield",
            title=u"My field",
            description=u"My great field",
            source=self.dummy_source_vocab,
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": u"My field",
                "description": u"My great field",
                "factory": "Choice",
                "enum": ["foo", "bar"],
                "enumNames": ["Foo", "Bar"],
                "choices": [("foo", "Foo"), ("bar", "Bar")],
                "vocabulary": {"@id": "http://nohost/plone/@sources/myfield"},
            },
            adapter.get_schema(),
        )

    def test_collection(self):
        field = schema.List(
            title=u"My field",
            description=u"My great field",
            min_length=1,
            value_type=schema.TextLine(
                title=u"Text", description=u"Text field", default=u"Default text"
            ),
            default=["foobar"],
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "array",
                "title": u"My field",
                "description": u"My great field",
                "factory": "List",
                "default": ["foobar"],
                "minItems": 1,
                "uniqueItems": False,
                "additionalItems": True,
                "items": {
                    "type": "string",
                    "title": u"Text",
                    "description": u"Text field",
                    "factory": "Text line (String)",
                    "default": u"Default text",
                },
            },
            adapter.get_schema(),
        )

        # Test Tuple
        field = schema.Tuple(title=u"My field", value_type=schema.Int(), default=(1, 2))
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "array",
                "title": u"My field",
                "description": u"",
                "factory": "Tuple",
                "uniqueItems": True,
                "additionalItems": True,
                "items": {
                    "title": u"",
                    "description": u"",
                    "type": "integer",
                    "factory": "Integer",
                },
                "default": (1, 2),
            },
            adapter.get_schema(),
        )

        # Test Set
        field = schema.Set(title=u"My field", value_type=schema.TextLine())
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "array",
                "title": u"My field",
                "description": u"",
                "factory": "Multiple Choice",
                "uniqueItems": True,
                "additionalItems": True,
                "items": {
                    "title": u"",
                    "description": u"",
                    "factory": "Text line (String)",
                    "type": "string",
                },
            },
            adapter.get_schema(),
        )

        # List of choices
        field = schema.List(
            __name__="myfield",
            title=u"My field",
            value_type=schema.Choice(vocabulary=self.dummy_vocabulary),
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "array",
                "title": u"My field",
                "description": u"",
                "factory": "List",
                "uniqueItems": True,
                "additionalItems": True,
                "items": {
                    "title": u"",
                    "description": u"",
                    "factory": "Choice",
                    "type": "string",
                    "enum": ["foo", "bar"],
                    "enumNames": ["Foo", "Bar"],
                    "choices": [("foo", "Foo"), ("bar", "Bar")],
                    "vocabulary": {"@id": "http://nohost/plone/@sources/"},
                },
            },
            adapter.get_schema(),
        )

    def test_object(self):
        field = schema.Object(
            title=u"My field", description=u"My great field", schema=IDummySchema
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "object",
                "title": u"My field",
                "description": u"My great field",
                "factory": "File",
                "properties": {
                    "field1": {
                        "title": u"Foo",
                        "description": u"",
                        "factory": u"Yes/No",
                        "type": "boolean",
                    },
                    "field2": {
                        "title": u"Bar",
                        "description": u"",
                        "factory": u"Text line (String)",
                        "type": "string",
                    },
                },
            },
            adapter.get_schema(),
        )

    def test_richtext(self):
        field = RichText(title=u"My field", description=u"My great field")
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": u"My field",
                "factory": u"Rich Text",
                "description": u"My great field",
                "widget": "richtext",
            },
            adapter.get_schema(),
        )

    def test_date(self):
        field = schema.Date(
            title=u"My field", description=u"My great field", default=date(2016, 1, 1)
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": u"My field",
                "factory": u"Date",
                "description": u"My great field",
                "default": date(2016, 1, 1),
                "widget": u"date",
            },
            adapter.get_schema(),
        )

    def test_datetime(self):
        field = schema.Datetime(title=u"My field", description=u"My great field")
        adapter = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        )

        self.assertEqual(
            {
                "type": "string",
                "title": u"My field",
                "factory": u"Date/Time",
                "description": u"My great field",
                "widget": u"datetime",
            },
            adapter.get_schema(),
        )
