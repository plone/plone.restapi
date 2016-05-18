# -*- coding: utf-8 -*-
"""Utils for jsonschema."""
from collections import OrderedDict

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.schema import getFieldsInOrder

from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.interfaces import IBehavior
from plone.supermodel.interfaces import FIELDSETS_KEY
from Products.CMFCore.utils import getToolByName

from plone.restapi.types.interfaces import IJsonSchemaProvider


def non_fieldset_fields(schema):
    fieldset_fields = []
    fieldsets = schema.queryTaggedValue(FIELDSETS_KEY, [])

    for fieldset in fieldsets:
        fieldset_fields.extend(fieldset.fields)

    fields = [info[0] for info in getFieldsInOrder(schema)]
    return [f for f in fields if f not in fieldset_fields]


def get_ordered_fields(fti):
    # this code is much complicated because we have to get sure
    # we get the fields in the order of the fieldsets
    # the order of the fields in the fieldsets can differ
    # of the getFieldsInOrder(schema) order...
    # that's because fields from different schemas
    # can take place in the same fieldset
    schema = fti.lookupSchema()
    fieldset_fields = {}
    ordered_fieldsets = ['default']
    for fieldset in schema.queryTaggedValue(FIELDSETS_KEY, []):
        ordered_fieldsets.append(fieldset.__name__)
        fieldset_fields[fieldset.__name__] = fieldset.fields

    fieldset_fields['default'] = non_fieldset_fields(schema)

    # Get the behavior fields
    fields = getFieldsInOrder(schema)
    for behavior_id in fti.behaviors:
        schema = getUtility(IBehavior, behavior_id).interface
        if not IFormFieldProvider.providedBy(schema):
            continue

        fields.extend(getFieldsInOrder(schema))
        for fieldset in schema.queryTaggedValue(FIELDSETS_KEY, []):
            fieldset_fields.setdefault(fieldset.__name__, []).extend(
                fieldset.fields)
            ordered_fieldsets.append(fieldset.__name__)

        fieldset_fields['default'].extend(non_fieldset_fields(schema))

    ordered_fields = []
    for fieldset in ordered_fieldsets:
        ordered_fields.extend(fieldset_fields[fieldset])

    fields.sort(key=lambda field: ordered_fields.index(field[0]))
    return fields


def get_fields_from_schema(schema, context, request, prefix='',
                           excluded_fields=None):
    """Get jsonschema from zope schema."""
    fields_info = OrderedDict()
    if excluded_fields is None:
        excluded_fields = []

    for fieldname, field in getFieldsInOrder(schema):
        if fieldname not in excluded_fields:
            adapter = getMultiAdapter(
                (field, context, request),
                interface=IJsonSchemaProvider)

            adapter.prefix = prefix
            if prefix:
                fieldname = '.'.join([prefix, fieldname])

            fields_info[fieldname] = adapter.get_schema()

    return fields_info


def get_jsonschema_for_fti(fti, context, request, excluded_fields=None):
    """Get jsonschema for given fti."""
    fields_info = OrderedDict()
    if excluded_fields is None:
        excluded_fields = []

    required = []
    for fieldname, field in get_ordered_fields(fti):
        if fieldname not in excluded_fields:
            adapter = getMultiAdapter(
                (field, context, request),
                interface=IJsonSchemaProvider)
            # get name from z3c.form field to have full name (behavior)
            fields_info[fieldname] = adapter.get_schema()
            if field.required:
                required.append(fieldname)

    return {
        'type': 'object',
        'title': fti.Title(),
        'properties': fields_info,
        'required': required,
    }


def get_jsonschema_for_portal_type(portal_type, context, request,
                                   excluded_fields=None):
    """Get jsonschema for given portal type name."""
    ttool = getToolByName(context, 'portal_types')
    fti = ttool[portal_type]
    return get_jsonschema_for_fti(
        fti, context, request, excluded_fields=excluded_fields)
