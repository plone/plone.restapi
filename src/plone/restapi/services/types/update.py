# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IPloneRestapiLayer
from plone.restapi.services import Service
from plone.restapi.types.utils import serializeSchema
from plone.supermodel.interfaces import FIELDSETS_KEY
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.publisher.interfaces import IPublishTraverse
import plone.protect.interfaces


@implementer(IPublishTraverse)
class TypesUpdate(Service):
    def __init__(self, context, request):
        super(TypesUpdate, self).__init__(context, request)
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
        if len(self.params) == 1:
            name = self.params.pop(0)
        elif len(self.params) == 2:
            name = self.params.pop(0)
            fname = self.params.pop(0)
            if "fields" in data:
                return self.reply_for_fieldset(name, fname, data)
            return self.reply_for_field(name, fname, data)
        else:
            raise BadRequest("Too many parameters")

        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )

        # Get content type SchemaContext
        context = context.publishTraverse(self.request, name)

        # Update Fieldset properties
        fieldsets = data.get("fieldsets", [])
        for fieldset in fieldsets:
            fname = fieldset.get("id")
            self.reply_for_fieldset(name, fname, fieldset)

        # Update Field properties
        properties = data.get("properties", {})
        for key, value in properties.items():
            self.reply_for_field(name, key, value)
        return self.reply_no_content()

    def reply_for_fieldset(self, name, fieldset_name, data):
        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )

        # Get content type SchemaContext
        context = context.publishTraverse(self.request, name)

        fieldsets = context.schema.queryTaggedValue(FIELDSETS_KEY, [])
        for idx, fieldset in enumerate(fieldsets):
            if fieldset_name != fieldset.__name__:
                continue

            fieldset.label = data.get(
                'title', fieldset.label)
            fieldset.description = data.get(
                'description', fieldset.description)

            for field_name in data.get('fields', []):
                if field_name not in context.schema:
                    continue

                field = context.publishTraverse(self.request, field_name)
                order = queryMultiAdapter(
                    (field, self.request), name='changefieldset')
                order.change(idx + 1)

        serializeSchema(context.schema)
        return self.reply_no_content()

    def reply_for_field(self, name, field_name, data):
        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )

        # Get content type SchemaContext
        context = context.publishTraverse(self.request, name)

        # Get FieldContext
        field = context.publishTraverse(self.request, field_name)

        # Update field properties
        for key, value in data.items():
            if hasattr(field.field, key):
                setattr(field.field, key, value)

        serializeSchema(context.schema)
        return self.reply_no_content()
