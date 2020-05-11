# -*- coding: utf-8 -*-
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
from plone.dexterity.utils import getAdditionalSchemata
from plone.restapi.serializer.converters import IJsonCompatible
from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.supermodel.utils import mergedTaggedValueDict
from Products.CMFCore.utils import getToolByName
from z3c.form import form as z3c_form
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate


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

    form = SchemaForm(context, request)
    form.updateFieldsFromSchemata()
    return form


def iter_fields(fieldsets):
    """Iterate over a flat list of fields, given a list of fieldset dicts
    as returned by `get_fieldsets`.
    """
    for fieldset in fieldsets:
        for field in fieldset["fields"]:
            yield field


def get_form_fieldsets(form):
    """ Get fieldsets from form
    """
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
            }
        )

    # Additional fieldsets (AKA z3c.form groups)
    for group in getattr(form, "groups", []):
        fieldset = {
            "id": group.__name__,
            "title": translate(group.label, context=getRequest()),
            "fields": list(group.fields.values()),
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


def get_jsonschema_for_fti(fti, context, request, excluded_fields=None):
    """Build a complete JSON schema for the given FTI.
    """
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

    # Determine required fields
    required = []
    for field in iter_fields(fieldsets):
        if field.field.required:
            required.append(field.field.getName())

    # Include field modes
    for field in iter_fields(fieldsets):
        if field.mode:
            properties[field.field.getName()]["mode"] = field.mode

    return {
        "type": "object",
        "title": translate(fti.Title(), context=getRequest()),
        "properties": IJsonCompatible(properties),
        "required": required,
        "fieldsets": get_fieldset_infos(fieldsets),
        "layouts": getattr(fti, "view_methods", []),
    }


def get_jsonschema_for_portal_type(portal_type, context, request, excluded_fields=None):
    """Build a complete JSON schema for the given portal_type.
    """
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
