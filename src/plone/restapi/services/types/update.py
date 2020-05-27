# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from plone.restapi.types.utils import get_jsonschema_for_portal_type
from plone.restapi.types.utils import update_defaults_for_portal_type
from plone.restapi.services.types.get import TypesInfo
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory

from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.deserializer import json_body


def check_security(context):
    # Only expose type information to authenticated users
    portal_membership = getToolByName(context, "portal_membership")
    if portal_membership.isAnonymousUser():
        raise Unauthorized

# @implementer(IExpandableElement)
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
