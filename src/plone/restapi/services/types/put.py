# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IPloneRestapiLayer
from plone.restapi.services import Service
from plone.restapi.types.utils import add_field
from plone.restapi.types.utils import add_fieldset
from plone.restapi.types.utils import delete_field
from plone.restapi.types.utils import delete_fieldset
from plone.restapi.types.utils import get_field_fieldset_index
from plone.restapi.types.utils import get_fieldset_index
from plone.restapi.types.utils import get_fieldset_infos
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import getAdditionalSchemata
from plone.restapi.types.utils import iter_fields
from plone.restapi.types.utils import serializeSchema
from plone.restapi.types.utils import sortedFields
from plone.supermodel.interfaces import FIELDSETS_KEY
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.container.contained import notifyContainerModified
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.publisher.interfaces import IPublishTraverse
import plone.protect.interfaces


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
            additional_schemata = tuple(
                getAdditionalSchemata(portal_type=fti.id))
            fti_fieldsets = get_fieldsets(
                self.context, self.request, schema, additional_schemata)

        # check for additional missed fieldsets
        fti_fieldset_ids = [fti_fset['id'] for fti_fset in fti_fieldsets]
        additional_fieldsets = schema.queryTaggedValue(FIELDSETS_KEY, [])
        for idx, fieldset in enumerate(additional_fieldsets):
            if fieldset.__name__ not in fti_fieldset_ids:
                props = {
                    'title': fieldset.label,
                    'id': fieldset.__name__,
                    'fields': fieldset.fields
                }
                fti_fieldsets.insert(idx + 1, props)

        for fieldset in fti_fieldsets:
            for field in fieldset['fields']:
                fieldinfo = fields[field.field.getName()]

                # skip over behavior fields
                behavior = fieldinfo.get(
                    'behavior', context.schema.__identifier__)
                if behavior != context.schema.__identifier__:
                    continue

                # remove fields
                if field.field.getName() not in iter_fields((fieldsets)):
                    delete_field(context, self.request, field.field.getName())

        new_order = []
        fti_fields = iter_fields(get_fieldset_infos(fti_fieldsets))
        for fieldset in fieldsets:
            # check if any new fieldsets
            fti_fieldset_ids = [fti_fset['id'] for fti_fset in fti_fieldsets]
            if fieldset['id'] not in fti_fieldset_ids:
                add_fieldset(context, self.request, fieldset)

            # TODO: what to do if fieldset repeats itself
            fieldset_index = get_fieldset_index(fieldset['id'], schema)

            # currently can reorder only non behavioral fieldsets
            for fset in additional_fieldsets:
                if fieldset['id'] == fset.__name__:
                    new_order.append(fset)

            position = -1
            for field in fieldset['fields']:
                fieldinfo = fields[field]
                behavior = fieldinfo.get(
                    'behavior', context.schema.__identifier__)
                if behavior != context.schema.__identifier__:
                    continue

                if field not in fti_fields and field not in context.schema:
                    # add new fields
                    fieldinfo['name'] = field
                    add_field(context, self.request, fieldinfo,
                              fieldset_index, required)

                fieldContext = context.publishTraverse(self.request, field)
                order = fieldContext.publishTraverse(self.request, 'order')
                changeFieldset = fieldContext.publishTraverse(self.request,
                                                              'changefieldset')

                if field in [finfo[0] for finfo in sortedFields(schema)]:
                    position += 1

                # change fieldset
                if fieldset_index != get_field_fieldset_index(field, fti_fieldsets): # noqa
                    changeFieldset(fieldset_index)

                # order
                order.move(position, fieldset_index)

                # set field default values
                context.schema[field].default = fields[field].get('default')

        fti_fieldset_ids = [fti_fset['id'] for fti_fset in fti_fieldsets]
        fieldset_ids = [fset['id'] for fset in fieldsets]
        fieldsets_to_remove = set(fti_fieldset_ids) - set(fieldset_ids)
        if len(fieldsets_to_remove) > 0:
            # remove fieldsets
            for fset in list(fieldsets_to_remove):
                delete_fieldset(context, self.request, fset)

        # set the new fieldset order
        context.schema.setTaggedValue(FIELDSETS_KEY, new_order)
        notifyContainerModified(context.schema)
        serializeSchema(context.schema)

        return self.reply_no_content()
