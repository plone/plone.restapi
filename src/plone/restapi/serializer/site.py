# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
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
        result['member'] = [
            getMultiAdapter((member, self.request), ISerializeToJsonSummary)()
            for member in self.context.objectValues()
            if IContentish.providedBy(member)
        ]
        return result
