# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.contentlisting.interfaces import IContentListing
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import IContentListingSerializer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.supermodel.utils import mergedTaggedValueDict
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import Interface
from zope.interface import implementer
from zope.schema import getFields
from zope.security.interfaces import IPermission


@implementer(ISerializeToJson)
@adapter(IDexterityContent, Interface)
class SerializeToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.permission_cache = {}

    def __call__(self):
        result = {
            '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            '@id': self.context.absolute_url(),
            '@type': self.context.portal_type,
            'parent': {
                '@id': aq_parent(aq_inner(self.context)).absolute_url(),
                'title': aq_parent(aq_inner(self.context)).title,
                'description': aq_parent(aq_inner(self.context)).description
            },
            'created': json_compatible(self.context.created()),
            'modified': json_compatible(self.context.modified()),
            'UID': self.context.UID(),
        }

        for schema in iterSchemata(self.context):

            read_permissions = mergedTaggedValueDict(
                schema, READ_PERMISSIONS_KEY)

            for name, field in getFields(schema).items():

                if not self.check_permission(read_permissions.get(name)):
                    continue

                serializer = queryMultiAdapter(
                    (field, self.context, self.request),
                    IFieldSerializer)
                value = serializer()
                result[json_compatible(name)] = value

        return result

    def check_permission(self, permission_name):
        if permission_name is None:
            return True

        if permission_name not in self.permission_cache:
            permission = queryUtility(IPermission,
                                      name=permission_name)
            if permission is None:
                self.permission_cache[permission_name] = True
            else:
                sm = getSecurityManager()
                self.permission_cache[permission_name] = bool(
                    sm.checkPermission(permission.title, self.context))
        return self.permission_cache[permission_name]


@implementer(ISerializeToJson)
@adapter(IDexterityContainer, Interface)
class SerializeFolderToJson(SerializeToJson):

    def __call__(self):
        result = super(SerializeFolderToJson, self).__call__()

        members = self.context.objectValues() or []
        result['member'] = getMultiAdapter(
            (IContentListing(members), self.request),
            IContentListingSerializer)()

        return result
