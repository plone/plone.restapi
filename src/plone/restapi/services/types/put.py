# -*- coding: utf-8 -*-
import plone.protect.interfaces
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.container.contained import notifyContainerModified
from zope.event import notify
from zope.interface import noLongerProvides
from zope.interface import implementer
from zope.interface import alsoProvides
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory
from zExceptions import BadRequest
from Products.CMFCore.utils import getToolByName
from plone.i18n.normalizer import idnormalizer
from plone.restapi.interfaces import IPloneRestapiLayer
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.types.utils import getAdditionalSchemata
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import iter_fields
from plone.restapi.types.utils import get_fieldset_infos
from plone.restapi.types.utils import serializeSchema
from plone.schemaeditor.utils import SchemaModifiedEvent
from plone.supermodel.interfaces import FIELDSETS_KEY


@implementer(IPublishTraverse)
class TypesPut(Service):
    def __init__(self, context, request):
        super(TypesPut, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        if not self.params:
            raise BadRequest("Missing parameter typename")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(
                self.request,
                plone.protect.interfaces.IDisableCSRFProtection
            )

        # Make sure we get the right dexterity-types adapter
        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        data = json_body(self.request)
        name = self.params.pop()
        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )
        context = context.publishTraverse(self.request, name)

        required = data.get('required', [])
        fieldsets = data.get('fieldsets', [])
        fields = data.get('properties')
        view_methods = data.get('layouts', [])
        title = data['title']

        ttool = getToolByName(context, "portal_types")
        fti = ttool[name]

        # set view methods
        fti.view_methods = tuple(view_methods)

        # set title
        fti.title = title

        try:
            schema = fti.lookupSchema()
        except AttributeError:
            schema = None
            fti_fieldsets = ()
            additional_schemata = ()
        else:
            additional_schemata = tuple(getAdditionalSchemata(portal_type=fti.id))
            fti_fieldsets = get_fieldsets(self.context, self.request,
                                          schema, additional_schemata)

        # check for additional missed fieldsets
        additional_fieldsets = schema.queryTaggedValue(FIELDSETS_KEY, [])
        for idx, fieldset in enumerate(additional_fieldsets):
            if fieldset.__name__ not in [fti_fset['id'] for fti_fset in fti_fieldsets]:
                props = {
                    'title': fieldset.label,
                    'id': fieldset.__name__,
                    'fields': fieldset.fields
                }
                fti_fieldsets.insert(idx + 1, props)

        for fieldset in fti_fieldsets:
            for field in fieldset['fields']:
                if field.field.getName() not in iter_fields((fieldsets)):
                    # remove fields
                    delete_field(context, self.request, field.field.getName())

        new_order = []
        fti_fields = iter_fields(get_fieldset_infos(fti_fieldsets))
        for fieldset in fieldsets:
            # TODO: if fieldset id repeats itself, use last occurrence for idx
            fieldset_index = fieldsets.index(fieldset)
            # fieldset_index = get_last_index_for_fieldset(fieldset['id'], fieldsets)

            # check if any new fieldsets
            if fieldset['id'] not in [fti_fset['id'] for fti_fset in fti_fieldsets]:
                add_fieldset(context, self.request, fieldset)

            # currently can reorder only non behavioral fieldsets
            for fset in additional_fieldsets:
                if fieldset['id'] == fset.__name__:
                    new_order.append(fset)

            for idx, field in enumerate(fieldset['fields']):
                fieldinfo = fields[field]
                if fieldinfo.get('behavior') != context.schema.__identifier__:
                    continue

                if field not in fti_fields and field not in context.schema:
                    # add new fields
                    fieldinfo['name'] = field
                    add_field(context, self.request, fieldinfo, fieldset_index, required)

                try:
                    fieldContext = context.publishTraverse(self.request, field)
                    order = fieldContext.publishTraverse(self.request, 'order')
                    changeFieldset = fieldContext.publishTraverse(self.request,
                                                            'changefieldset')
                except Exception:
                    continue

                # change fieldset
                if fieldset_index != get_field_fieldset_index(field, fti_fieldsets):
                    changeFieldset(fieldset_index)

                # order
                order.move(idx, fieldset_index)

                # set field default values
                context.schema[field].default = fields[field].get('default')

        fieldsets_to_remove = set([fti_fset['id'] for fti_fset in fti_fieldsets]) - set([fset['id'] for fset in fieldsets])
        if len(fieldsets_to_remove) > 0:
            # remove fieldsets
            for fset in list(fieldsets_to_remove):
                delete_fieldset(context, self.request, fset)

        serializeSchema(context.schema)

        # set the new fieldset order
        context.schema.setTaggedValue(FIELDSETS_KEY, new_order)
        notifyContainerModified(context.schema)
        notify(SchemaModifiedEvent(self.context))

        return self.reply_no_content()


def delete_field(context, request, field):
    fieldContext = context.publishTraverse(request, field)
    delete = queryMultiAdapter((fieldContext, request), name="delete")
    delete()


def delete_fieldset(context, request, fieldset):
    request.form['name'] = fieldset
    delete = queryMultiAdapter((context, request),
                               name="delete-fieldset")
    delete()


def add_fieldset(context, request, fieldset):
    tid = fieldset.get("id", None)
    title = fieldset.get("title", None)
    description = fieldset.get("description", None)

    if not tid:
        tid = idnormalizer.normalize(title).replace("-", "_")

    add = queryMultiAdapter((context, request),
                            name="add-fieldset")
    properties = {
        "label": title,
        "__name__": tid,
        "description": description
    }
    fieldset = add.form_instance.create(data=properties)
    add.form_instance.add(fieldset)


def add_field(context, request, field, fieldset_index, required):
    widget = field.get('widget', None)
    name = field.get('name')

    klass = None
    vocabulary = queryUtility(IVocabularyFactory, name='Fields')
    for term in vocabulary(context):
        if widget in (term.title, term.token):
            klass = term.value

    if not klass:
        raise BadRequest("Missing parameter widget")

    request.form["fieldset_id"] = fieldset_index
    add = queryMultiAdapter((context, request), name="add-field")
    properties = {
        "title": field.get('title'),
        "__name__": name,
        "description": field.get('description'),
        "factory": klass,
        "required": name in required
    }
    created_field = add.form_instance.create(data=properties)
    add.form_instance.add(created_field)


def get_field_fieldset_index(fieldname, fieldsets):
    for idx, fieldset in enumerate(fieldsets):
        for field in fieldset['fields']:
            if field.field.getName() == fieldname:
                return idx


def get_last_index_for_fieldset(fieldsetname, fieldsets):
    ids = [fieldset['id'] for fieldset in fieldsets]
    index = 0
    repeated = False
    for idx, id in enumerate(ids):
        if fieldsetname == id:
            index = idx
            if repeated:
                index -= 1
            repeated = True
    return index
