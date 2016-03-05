# -*- coding: utf-8 -*-
from plone.app.contentlisting.interfaces import IContentListing
from plone.restapi.interfaces import IContentListingSerializer
from plone.restapi.interfaces import ISerializeToJson
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(IPloneSiteRoot, Interface)
class SerializeSiteRootToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        result = {
            '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            '@id': self.context.absolute_url(),
            '@type': 'Plone Site',
            'parent': {},
        }

        members = [obj for obj in self.context.objectValues()
                   if IContentish.providedBy(obj)]

        result['member'] = getMultiAdapter(
            (IContentListing(members), self.request),
            IContentListingSerializer)()

        return result
