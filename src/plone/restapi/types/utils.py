"""Utils to translate FTIs / zope.schema interfaces to JSON schemas.

The basic idea here is to instantiate a minimal z3c form, and then have
plone.autoform work its magic on it to process all the fields, and apply
any p.autoform directives (fieldsets, field modes, omitted fields, field
permissions, widgets).

Also schema interface inheritance (IRO) and additional schemata from behaviors
are factored into how the final resulting fieldsets are composed.

This approach should ensure that all these directives get respected and
processed the same way they would for a server-rendered form.
"""

from collections import OrderedDict
from copy import copy
from plone.autoform.form import AutoExtensibleForm
from plone.autoform.interfaces import IParameterizedWidget
from plone.autoform.interfaces import WIDGETS_KEY
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from plone.i18n.normalizer import idnormalizer
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.serializer.converters import IJsonCompatible
from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.supermodel import serializeModel
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.utils import mergedTaggedValueDict
from plone.supermodel.utils import syncSchema
from Products.CMFCore.utils import getToolByName
from z3c.form import form as z3c_form
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from plone.app.multilingual.dx.interfaces import MULTILINGUAL_KEY
from plone.supermodel.utils import mergedTaggedValueList

try:
    # Plone 5.1+
    from plone.dexterity.schema import splitSchemaName
except ImportError:
    # Plone 4.3
    from plone.dexterity.utils import splitSchemaName


_marker = []  # Create a new marker object.

FIELD_PROPERTIES_MAPPING = {
    "minLength": "min_length",
    "maxLength": "max_length",
    "minItems": "min_length",
    "maxItems": "max_length",
    "minimum": "min",
    "maximum": "max",
}


@implementer(IDexterityContent)
class FakeDXContext:
    """Fake DX content class, so we can re-use the DX field deserializers"""


def create_form(context, request, base_schema, additional_schemata=None):
    """Create a minimal, standalone z3c form and run the field processing
    logic of plone.autoform on it.
    """
    if additional_schemata is None:
        additional_schemata = ()

    class SchemaForm(AutoExtensibleForm, z3c_form.AddForm):
        schema = base_schema
        additionalSchemata = additional_schemata
        ignoreContext = True
        ignorePrefix = True

    form = SchemaForm(context, request)
    form.updateFieldsFromSchemata()
    return form


def iter_fields(fieldsets):
    """Iterate over a flat list of fields, given a list of fieldset dicts
    as returned by `get_fieldsets`.
    """
    for fieldset in fieldsets:
        yield from fieldset["fields"]


def get_form_fieldsets(form):
    """Get fieldsets from form"""
    fieldsets = []
    form_fields = getattr(form, "fields", {})
    fields_values = list(form_fields.values())
    if form_fields:
        fieldsets.append(
            {
                "id": "default",
                "title": translate(
                    "label_schema_default",
                    default="Default",
                    domain="plone",
                    context=getRequest(),
                ),
                "fields": fields_values,
                "behavior": "plone",
            }
        )

    # Additional fieldsets (AKA z3c.form groups)
    for group in getattr(form, "groups", []):
        fieldset = {
            "id": group.__name__,
            "title": translate(group.label, context=getRequest()),
            "description": translate(group.description, context=getRequest())
            if group.description is not None
            else "",
            "fields": list(group.fields.values()),
            "behavior": "plone",
        }
        fieldsets.append(fieldset)
    return fieldsets


def get_fieldsets(context, request, schema, additional_schemata=None):
    """Given a base schema, and optionally some additional schemata,
    build a list of fieldsets with the corresponding z3c.form fields in them.
    """
    form = create_form(context, request, schema, additional_schemata)
    return get_form_fieldsets(form)


def get_fieldset_infos(fieldsets):
    """Given a list of fieldset dicts as returned by `get_fieldsets()`,
    return a list of fieldset info dicts that contain the (short) field name
    instead of the actual field instance.
    """
    fieldset_infos = []
    for fieldset in fieldsets:
        fs_info = copy(fieldset)
        fs_info["fields"] = [f.field.getName() for f in fs_info["fields"]]
        fieldset_infos.append(fs_info)
    return fieldset_infos


def get_jsonschema_properties(
    context, request, fieldsets, prefix="", excluded_fields=None
):
    """Build a JSON schema 'properties' list, based on a list of fieldset
    dicts as returned by `get_fieldsets()`.
    """
    properties = OrderedDict()
    if excluded_fields is None:
        excluded_fields = []

    for field in iter_fields(fieldsets):
        fieldname = field.field.getName()
        if fieldname not in excluded_fields:
            # We need to special case relatedItems not to render choices
            # so we try a named adapter first and fallback to unnamed ones.
            adapter = queryMultiAdapter(
                (field.field, context, request),
                interface=IJsonSchemaProvider,
                name=field.__name__,
            )

            adapter = adapter or getMultiAdapter(
                (field.field, context, request), interface=IJsonSchemaProvider
            )

            adapter.prefix = prefix
            if prefix:
                fieldname = ".".join([prefix, fieldname])

            properties[fieldname] = adapter.get_schema()

    return properties


def get_widget_params(schemas):
    params = {}
    for schema in schemas:
        if not schema:
            continue
        tagged_values = mergedTaggedValueDict(schema, WIDGETS_KEY)
        for field_name in schema:
            widget = tagged_values.get(field_name)
            if IParameterizedWidget.providedBy(widget) and widget.params:
                params[field_name] = {}
                for k, v in widget.params.items():
                    if callable(v):
                        v = v()
                    params[field_name][k] = v
    return params


def get_multilingual_directives(schemas):
    params = {}
    for schema in schemas:
        if not schema:
            continue
        tagged_values = mergedTaggedValueList(schema, MULTILINGUAL_KEY)
        result = {field_name: value for _, field_name, value in tagged_values}

        for field_name, value in result.items():
            params[field_name] = {}
            params[field_name]["language_independent"] = value
    return params


def get_jsonschema_for_fti(fti, context, request, excluded_fields=None):
    """Build a complete JSON schema for the given FTI."""
    if excluded_fields is None:
        excluded_fields = []

    # We try..except lookupSchema here, so we still get FTI information
    # through /@types/{typeid} for non-DX type, notably the "Plone Site" type.
    try:
        schema = fti.lookupSchema()
    except AttributeError:
        schema = None
        fieldsets = ()
        additional_schemata = ()
    else:
        additional_schemata = tuple(getAdditionalSchemata(portal_type=fti.id))
        fieldsets = get_fieldsets(context, request, schema, additional_schemata)

    # Build JSON schema properties
    properties = get_jsonschema_properties(
        context, request, fieldsets, excluded_fields=excluded_fields
    )

    required = []
    for field in iter_fields(fieldsets):
        name = field.field.getName()
        # Determine required fields
        if field.field.required:
            required.append(name)

        # Include field modes
        if field.mode:
            properties[name]["mode"] = field.mode

        # Include behavior
        if name in properties:
            behavior = queryUtility(IBehavior, name=field.interface.__identifier__)
            properties[name]["behavior"] = (
                getattr(behavior, "name", None) or field.interface.__identifier__
            )

    return {
        "type": "object",
        "title": translate(fti.Title(), context=getRequest()),
        "properties": IJsonCompatible(properties),
        "required": required,
        "fieldsets": get_fieldset_infos(fieldsets),
        "layouts": getattr(fti, "view_methods", []),
    }


def get_jsonschema_for_portal_type(portal_type, context, request, excluded_fields=None):
    """Build a complete JSON schema for the given portal_type."""
    ttool = getToolByName(context, "portal_types")
    fti = ttool[portal_type]
    return get_jsonschema_for_fti(
        fti, context, request, excluded_fields=excluded_fields
    )


def get_vocab_like_url(endpoint, locator, context, request):
    try:
        context_url = context.absolute_url()
    except AttributeError:
        portal = getSite()
        context_url = portal.absolute_url()
    return "/".join((context_url, endpoint, locator))


def get_vocabulary_url(vocab_name, context, request):
    return get_vocab_like_url("@vocabularies", vocab_name, context, request)


def get_querysource_url(field, context, request):
    return get_vocab_like_url("@querysources", field.getName(), context, request)


def get_source_url(field, context, request):
    return get_vocab_like_url("@sources", field.getName(), context, request)


def serializeSchema(schema):
    """Taken from plone.app.dexterity.serialize
    Finds the FTI and model associated with a schema, and synchronizes
    the schema to the FTI model_source attribute.
    """

    # determine portal_type
    try:
        prefix, portal_type, schemaName = splitSchemaName(schema.__name__)
    except ValueError:
        # not a dexterity schema
        return

    # find the FTI and model
    fti = queryUtility(IDexterityFTI, name=portal_type)
    model = fti.lookupModel()

    # synchronize changes to the model
    syncSchema(schema, model.schemata[schemaName], overwrite=True)
    fti.model_source = serializeModel(model)


def get_info_for_type(context, request, name):
    """Get JSON info for the given portal type"""
    base_context = context

    # If context is not a dexterity content, use site root to get
    # the schema
    if not IDexterityContent.providedBy(context):
        base_context = getSite()

    schema = get_jsonschema_for_portal_type(name, base_context, request)

    if not hasattr(context, "schema"):
        return schema

    # Get the empty fieldsets
    existing = {f.get("id") for f in schema.get("fieldsets", [])}
    generated = set()
    for fieldset in context.schema.queryTaggedValue(FIELDSETS_KEY, []):
        name = fieldset.__name__
        generated.add(name)

        if name not in existing:
            info = get_info_for_fieldset(context, request, name)
            schema["fieldsets"].append(info)
            continue

    # Update fieldset behavior
    for idx, tab in enumerate(schema.get("fieldsets", [])):
        if tab.get("id") in generated:
            schema["fieldsets"][idx]["behavior"] = "plone.dexterity.schema.generated"

    return schema


def get_info_for_field(context, request, name):
    """Get JSON info for the given field name."""
    field = context.publishTraverse(request, name)
    adapter = queryMultiAdapter(
        (field.field, context, request), interface=IJsonSchemaProvider
    )

    schema = adapter.get_schema()
    schema["behavior"] = context.schema.__identifier__
    return IJsonCompatible(schema)


def get_info_for_fieldset(context, request, name):
    """Get JSON info for the given fieldset name."""
    properties = {}
    for fieldset in context.schema.queryTaggedValue(FIELDSETS_KEY, []):
        if name != fieldset.__name__:
            continue

        properties = {
            "id": fieldset.__name__,
            "title": fieldset.label,
            "description": fieldset.description,
            "fields": fieldset.fields,
            "behavior": "plone.dexterity.schema.generated",
        }
    return IJsonCompatible(properties)


def delete_field(context, request, name):
    field = context.publishTraverse(request, name)
    delete = queryMultiAdapter((field, request), name="delete")
    delete()


def delete_fieldset(context, request, name):
    """Taken from plone.schemaeditor 2.x `DeleteFieldset`"""
    new_fieldsets = []
    fieldsets = context.schema.queryTaggedValue(FIELDSETS_KEY, [])
    for fieldset in fieldsets:
        if fieldset.__name__ == name:
            # Can't delete fieldsets with fields
            if fieldset.fields:
                return
            continue
        new_fieldsets.append(fieldset)

    # Nothing changed
    if len(fieldsets) == len(new_fieldsets):
        return

    context.schema.setTaggedValue(FIELDSETS_KEY, new_fieldsets)
    serializeSchema(context.schema)


def add_fieldset(context, request, data):
    name = data.get("id", None)
    title = data.get("title", None)
    description = data.get("description", None)

    if not name:
        name = idnormalizer.normalize(title).replace("-", "_")

    # Default is reserved
    if name == "default":
        return {}

    add = queryMultiAdapter((context, request), name="add-fieldset")
    properties = {"__name__": name, "label": title, "description": description}
    fieldset = add.form_instance.create(data=properties)
    add.form_instance.add(fieldset)

    return get_info_for_fieldset(context, request, name)


def add_field(context, request, data):
    factory = data.get("factory", None)
    title = data.get("title", None)
    description = data.get("description", None)
    required = data.get("required", False)
    name = data.get("id", None)
    if not name:
        name = idnormalizer.normalize(title).replace("-", "_")

    klass = None
    vocabulary = queryUtility(IVocabularyFactory, name="Fields")
    for term in vocabulary(context):
        if factory not in (term.title, term.token):
            continue

        klass = term.value
        break

    if not klass:
        raise BadRequest("Missing/Invalid parameter factory: %s" % factory)

    add = queryMultiAdapter((context, request), name="add-field")
    properties = {
        "title": title,
        "__name__": name,
        "description": description,
        "factory": klass,
        "required": required,
    }

    field = add.form_instance.create(data=properties)
    add.form_instance.add(field)

    return get_info_for_field(context, request, name)


def update_fieldset(context, request, data):
    name = data.get("id", None)
    title = data.get("title", None)
    description = data.get("description", None)
    fields = data.get("fields", None)

    if not name:
        name = idnormalizer.normalize(title).replace("-", "_")

    # We can only re-order fields within the default fieldset
    if name == "default":
        pos = 0
        for field_name in fields:
            if field_name not in context.schema:
                continue

            field = context.publishTraverse(request, field_name)
            order = queryMultiAdapter((field, request), name="order")
            order.move(pos, 0)
            pos += 1
        return

    # Update fieldset
    fieldsets = context.schema.queryTaggedValue(FIELDSETS_KEY, [])
    for idx, fieldset in enumerate(fieldsets):
        if name != fieldset.__name__:
            continue

        if title:
            fieldset.label = title

        if description:
            fieldset.description = description

        pos = 0
        for field_name in fields:
            if field_name not in context.schema:
                continue

            field = context.publishTraverse(request, field_name)
            order = queryMultiAdapter((field, request), name="order")
            order.move(pos, idx + 1)
            pos += 1


def update_field(context, request, data):
    field = context.publishTraverse(request, data.pop("id"))
    edit = queryMultiAdapter((field, request), name="edit")
    default = data.pop("default", _marker)

    properties = {}
    for key, value in data.items():
        key = FIELD_PROPERTIES_MAPPING.get(key, key)
        properties[key] = value

    # clear current min/max to avoid range errors
    if "min" in properties:
        edit.form_instance.field.min = None
    if "max" in properties:
        edit.form_instance.field.max = None

    edit.form_instance.updateFields()
    edit.form_instance.applyChanges(properties)

    if default is not _marker:
        fake_context = FakeDXContext()
        deserializer = queryMultiAdapter(
            (field.field, fake_context, request), IFieldDeserializer
        )
        setattr(field.field, "default", deserializer(default))
