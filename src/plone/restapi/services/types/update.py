# -*- coding: utf-8 -*-
import plone.protect.interfaces
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import noLongerProvides
from zope.interface import implementer
from zope.interface import alsoProvides
from zope.component import queryMultiAdapter
from zExceptions import BadRequest
from plone.restapi.services import Service
from plone.restapi.interfaces import IPloneRestapiLayer
from plone.restapi.deserializer import json_body
from plone.restapi.types.utils import serializeSchema


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

        if len(self.params) == 2:
            return self.reply_for_field()

        data = json_body(self.request)
        name = self.params.pop()
        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )

        context = context.publishTraverse(self.request, name)
        for key, value in data.items():
            if key in context.schema:
                context.schema[key].default = value
        serializeSchema(context.schema)

        return self.reply_no_content()

    def reply_for_field(self):
        data = json_body(self.request)

        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )

        # Get content type SchemaContext
        name = self.params.pop(0)
        context = context.publishTraverse(self.request, name)

        # Get FieldContext
        name = self.params.pop(0)
        context = context.publishTraverse(self.request, name)

        # Change tab
        fieldset_id = data.pop("fieldset_id", data.pop("fieldset_index", None))
        if fieldset_id is not None:
            tab = queryMultiAdapter(
                (context, self.request), name="changefieldset")
            tab.change(fieldset_id)

        # Re-order
        pos = data.pop("pos", None)
        if pos is not None:
            order = queryMultiAdapter(
                (context, self.request), name="order")
            order.move(pos, fieldset_id or -1)

        # Update field properties
        for key, value in data.items():
            if hasattr(context.field, key):
                setattr(context.field, key, value)
        serializeSchema(context.schema)

        return self.reply_no_content()
