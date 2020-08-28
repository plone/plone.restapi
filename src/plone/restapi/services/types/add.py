# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IPloneRestapiLayer
from plone.restapi.services import Service
from plone.restapi.types.utils import add_field
from plone.restapi.types.utils import add_fieldset
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.publisher.interfaces import IPublishTraverse
import plone.protect.interfaces


@implementer(IPublishTraverse)
class TypesPost(Service):
    """Creates a new field/fieldset"""

    def __init__(self, context, request):
        super(TypesPost, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        if not self.params:
            raise BadRequest("Missing parameter typename")

        data = json_body(self.request)

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        # Make sure we get the right dexterity-types adapter
        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        name = self.params.pop()
        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )
        context = context.publishTraverse(self.request, name)

        factory = data.get("factory", None)
        if not factory:
            raise BadRequest("Missing parameter: 'factory'")

        if factory == "fieldset":
            res = add_fieldset(context, self.request, data)
        else:
            res = add_field(context, self.request, data)

        self.request.response.setStatus(201)
        return res
