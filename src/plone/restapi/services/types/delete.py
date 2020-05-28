# -*- coding: utf-8 -*-
import plone.protect.interfaces
from plone.restapi.services import Service
from plone.restapi.interfaces import IPloneRestapiLayer
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.component import queryMultiAdapter
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import BadRequest


@implementer(IPublishTraverse)
class TypesDelete(Service):
    """ Deletes a field/fieldset from content type
    """
    def __init__(self, context, request):
        super(TypesDelete, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        if not self.params:
            raise BadRequest("Missing parameter typename")
        if len(self.params) > 2:
            raise BadRequest("Too many parameters")
        if len(self.params) < 2:
            raise BadRequest("Missing parameter fieldname")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(
                self.request,
                plone.protect.interfaces.IDisableCSRFProtection
            )

        # Make sure we don't get the right dexterity-types adapter
        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        name = self.params[0]
        field_name = self.params[1]

        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )
        # get content type SchemaContext
        context = context.publishTraverse(self.request, name)

        # get FieldContext
        context = context.publishTraverse(self.request, field_name)

        delete = context.publishTraverse(self.request, 'delete')
        delete()

        return self.reply_no_content()
