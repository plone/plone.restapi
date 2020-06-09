# -*- coding: utf-8 -*-
import plone.protect.interfaces
from zope.publisher.interfaces import IPublishTraverse
from zope.interface import noLongerProvides
from zope.interface import implementer
from zope.interface import alsoProvides
from zope.component import queryMultiAdapter
from zExceptions import BadRequest
from plone.restapi.services import Service
from plone.restapi.types.utils import get_jsonschema_for_fti
from plone.restapi.interfaces import IPloneRestapiLayer
from plone.restapi.deserializer import json_body
from Products.CMFCore.utils import getToolByName


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

        for key, value in data.items():
            for idx, field in enumerate(value['fields']):
                try:
                    fieldContext = context.publishTraverse(self.request, field)
                    order = fieldContext.publishTraverse(self.request, 'order')
                    changeFieldset = fieldContext.publishTraverse(self.request,
                    'changefieldset')
                except Exception:
                    continue

                ttool = getToolByName(context, "portal_types")
                fti = ttool[name]
                schema = get_jsonschema_for_fti(fti, self.context, self.request)
                fieldsets = schema['fieldsets']

                # get fieldset index
                for fieldset in fieldsets:
                    if key == fieldset['id']:
                        fieldset_index = fieldsets.index(fieldset)

                # change fieldset
                changeFieldset(fieldset_index)
                # order
                order.move(idx, fieldset_index)
        return self.reply_no_content()
