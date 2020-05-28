# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from plone.restapi.types.utils import update_defaults_for_portal_type
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse



def check_security(context):
    # Only expose type information to authenticated users
    portal_membership = getToolByName(context, "portal_membership")
    if portal_membership.isAnonymousUser():
        raise Unauthorized

@implementer(IPublishTraverse)
class TypesUpdate(Service):
    def __init__(self, context, request):
        super(TypesUpdate, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    @property
    def _get_record_name(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (dotted name of"
                "the record to be retrieved)"
            )

        return self.params[0]

    def reply(self):
        if self.params and len(self.params) > 0:
            # Modify schema for a specific type
            check_security(self.context)
            self.content_type = "application/json+schema"
            try:
                portal_type = self.params[0]
                body = json_body(self.request)

                update_defaults_for_portal_type(portal_type, self.context, self.request, body)
            except KeyError:
                self.content_type = "application/json"
                self.request.response.setStatus(404)
                return {
                    "type": "NotFound",
                    "message": 'Type "{}" could not be found.'.format(portal_type),
                }
        return self.reply_no_content()
