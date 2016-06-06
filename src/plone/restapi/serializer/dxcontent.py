# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.supermodel.utils import mergedTaggedValueDict
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface
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
        parent = aq_parent(aq_inner(self.context))
        parent_summary = getMultiAdapter(
            (parent, self.request), ISerializeToJsonSummary)()
        result = {
            # '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            '@id': self.context.absolute_url(),
            '@type': self.context.portal_type,
            'parent': parent_summary,
            'created': json_compatible(self.context.created()),
            'modified': json_compatible(self.context.modified()),
            'review_state': self._get_workflow_state(),
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

    def _get_workflow_state(self):
        wftool = getToolByName(self.context, 'portal_workflow')
        review_state = wftool.getInfoFor(
            ob=self.context, name='review_state', default=None)
        return review_state

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

    def _build_query(self):
        path = '/'.join(self.context.getPhysicalPath())
        query = {'path': {'depth': 1, 'query': path,
                 'sort_on': 'getObjPositionInParent'}}
        return query

    def __call__(self):
        folder_metadata = super(SerializeFolderToJson, self).__call__()

        query = self._build_query()

        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog(query)

        batch = HypermediaBatch(self.request, brains)

        result = folder_metadata
        result['@id'] = batch.canonical_url
        result['items_total'] = batch.items_total
        if batch.links:
            result['batching'] = batch.links

        result['items'] = [
            getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
            for brain in batch
        ]
        return result
