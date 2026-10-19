from plone.autoform import directives
from plone.namedfile.field import NamedBlobImage
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.restapi.types.utils import deserialize_schema_values
from plone.restapi.types.utils import FakeDXContext
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_for_schema
from plone.restapi.types.utils import SchemaValues
from plone.restapi.types.utils import serialize_schema_values
from plone.supermodel import model
from Products.CMFCore.utils import getToolByName
from unittest import TestCase
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import invariant
from zope.interface import provider
from zope.interface.exceptions import Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@provider(IContextSourceBinder)
def portal_types(context):
    tool = getToolByName(context, "portal_types")
    return SimpleVocabulary(
        [
            SimpleTerm(fti.getId(), fti.getId(), fti.Title())
            for fti in tool.listTypeInfo()
        ]
    )


class IRange(model.Schema):
    start = schema.Int(title="Start")
    end = schema.Int(title="End", required=False)

    @invariant
    def ordered(data):
        if data.end is not None and data.start > data.end:
            raise Invalid("Start must not be after end")


class IWithRange(model.Schema):
    range = schema.Object(title="Range", schema=IRange, required=False)


class ISettings(model.Schema):
    title = schema.TextLine(title="Title")
    kind = schema.Choice(title="Kind", values=("a", "b"), required=False)
    types = schema.List(
        title="Types",
        value_type=schema.Choice(source=portal_types),
        required=False,
    )
    created = schema.TextLine(title="Created", readonly=True, required=False)
    directives.mode(shown="display")
    shown = schema.TextLine(title="Shown", required=False)
    directives.mode(secret="hidden")
    secret = schema.TextLine(title="Secret", required=False)
    directives.omitted("internal")
    internal = schema.TextLine(title="Internal", required=False)

    @invariant
    def title_not_kind(data):
        if data.title == data.kind:
            raise Invalid("Title and kind must differ")


class TestSchemaValues(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_values_defaults_and_schema(self):
        values = SchemaValues(ISettings, {"title": "Hello"})
        self.assertTrue(ISettings.providedBy(values))
        self.assertEqual(values.title, "Hello")
        self.assertIsNone(values.kind)

    def test_acquires_site_tools(self):
        values = SchemaValues(ISettings, {}).__of__(self.portal)
        self.assertIsNotNone(getToolByName(values, "portal_types"))

    def test_bbb_alias(self):
        self.assertIs(FakeDXContext, SchemaValues)


class TestJsonSchemaForSchema(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_readonly_modes_and_required(self):
        result = get_jsonschema_for_schema(self.portal, self.request, ISettings)
        properties = result["properties"]
        self.assertEqual(result["type"], "object")
        # z3c.form leaves read-only schema fields out of forms.
        self.assertNotIn("created", properties)
        self.assertTrue(properties["shown"]["readOnly"])
        self.assertEqual(properties["shown"]["mode"], "display")
        # Hidden fields are still submitted by forms.
        self.assertNotIn("readOnly", properties["secret"])
        self.assertEqual(properties["secret"]["mode"], "hidden")
        self.assertNotIn("internal", properties)
        self.assertEqual(result["required"], ["title"])
        self.assertEqual(
            result["fieldsets"][0]["fields"],
            ["title", "kind", "types", "shown", "secret"],
        )

    def test_nested_object_schema(self):
        result = get_jsonschema_for_schema(self.portal, self.request, IWithRange)
        range_schema = result["properties"]["range"]
        self.assertEqual(range_schema["type"], "object")
        self.assertNotIn("factory", range_schema)
        self.assertEqual(set(range_schema["properties"]), {"start", "end"})
        self.assertEqual(range_schema["required"], ["start"])

    def test_file_objects_keep_legacy_shape(self):
        field = NamedBlobImage(title="Image")
        field.__name__ = "image"
        result = getMultiAdapter(
            (field, self.portal, self.request), IJsonSchemaProvider
        ).get_schema()
        self.assertEqual(result["factory"], "Image")
        self.assertNotIn("required", result)
        self.assertTrue(all(key.startswith("image.") for key in result["properties"]))


class TestSchemaValuesConversion(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def values(self, **data):
        current = {
            "title": "Hello",
            "kind": "a",
            "types": ["Document"],
            "created": "today",
            "internal": "x",
        }
        current.update(data)
        return SchemaValues(ISettings, current).__of__(self.portal)

    def test_serialize_all_fields_by_default(self):
        data = serialize_schema_values(self.values(), self.request, ISettings)
        self.assertEqual(data["title"], "Hello")
        self.assertEqual(data["kind"], {"token": "a", "title": None})
        self.assertEqual(data["types"], [{"token": "Document", "title": "Page"}])
        self.assertEqual(data["internal"], "x")

    def test_serialize_processed_fields(self):
        context = self.values()
        fieldsets = get_fieldsets(context, self.request, ISettings)
        data = serialize_schema_values(
            context, self.request, ISettings, fieldsets=fieldsets
        )
        self.assertNotIn("internal", data)

    def test_lenient_mode_skips_unknown_and_readonly(self):
        values, errors = deserialize_schema_values(
            self.portal,
            self.request,
            ISettings,
            {"title": "New", "created": "x", "unknown": 1},
        )
        self.assertEqual(errors, [])
        self.assertEqual(values, {"title": "New"})

    def test_strict_mode_reports_unknown_readonly_and_missing(self):
        fieldsets = get_fieldsets(self.portal, self.request, ISettings)
        values, errors = deserialize_schema_values(
            self.portal,
            self.request,
            ISettings,
            {"shown": "x", "internal": "x", "created": "x", "kind": "c"},
            fieldsets=fieldsets,
            partial=False,
            strict=True,
        )
        self.assertEqual(
            {error["field"] for error in errors},
            {"shown", "internal", "created", "kind", "title"},
        )

    def test_strict_partial_invariants_see_current_values(self):
        current = {"title": "a", "kind": "b"}
        values, errors = deserialize_schema_values(
            self.portal,
            self.request,
            ISettings,
            {"kind": "a"},
            current=current,
            strict=True,
        )
        self.assertEqual(errors[0]["message"], "Title and kind must differ")
        values, errors = deserialize_schema_values(
            self.portal,
            self.request,
            ISettings,
            {"title": "c"},
            current=current,
            strict=True,
        )
        self.assertEqual((values, errors), ({"title": "c"}, []))

    def test_choices_accept_tokens_and_term_dicts(self):
        values, errors = deserialize_schema_values(
            self.portal,
            self.request,
            ISettings,
            {"kind": {"token": "b"}, "types": ["Document", {"token": "Folder"}]},
            strict=True,
        )
        self.assertEqual(errors, [])
        self.assertEqual(values, {"kind": "b", "types": ["Document", "Folder"]})
