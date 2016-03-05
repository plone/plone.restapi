# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Products.Archetypes.interfaces import IBaseFolder
from Products.Archetypes.interfaces import IBaseObject
from plone.app.contentlisting.interfaces import IContentListing
from plone.restapi.interfaces import IContentListingSerializer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(IBaseObject, Interface)
class SerializeToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        result = {
            '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            '@id': self.context.absolute_url(),
            '@type': self.context.portal_type,
            'parent': {
                '@id': aq_parent(self.context).absolute_url(),
                'title': aq_parent(self.context).Title(),
                'description': aq_parent(self.context).Description()
            },
            'UID': self.context.UID(),
        }

        obj = self.context
        for field in obj.Schema().fields():

            if 'r' not in field.mode or not field.checkPermission('r', obj):
                continue

            name = field.getName()

            serializer = queryMultiAdapter(
                (field, self.context, self.request),
                IFieldSerializer)
            if serializer is not None:
                result[name] = serializer()

        return result


@implementer(ISerializeToJson)
@adapter(IBaseFolder, Interface)
class SerializeFolderToJson(SerializeToJson):

    def __call__(self):
        result = super(SerializeFolderToJson, self).__call__()

        members = self.context.objectValues() or []
        result['member'] = getMultiAdapter(
            (IContentListing(members), self.request),
            IContentListingSerializer)()

        return result
