# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot
from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from plone.restapi.interfaces import IAPIRequest
from zope.interface import alsoProvides
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapter
from ZPublisher.BaseRequest import DefaultPublishTraverse
from plone.restapi.interfaces import ISerializeToJson


class MarkAsApiRequest(SimpleItem):
    """Mark the @@json view with the IAPIRequest interface.
    """
    implements(IPublishTraverse)

    def publishTraverse(self, request, name):
        alsoProvides(self.request, IAPIRequest)
        return self.context


@adapter(IPloneSiteRoot, IAPIRequest)
class APISiteRootTraverser(DefaultPublishTraverse):

    def publishTraverse(self, request, name):
        self.request.response.setHeader('Content-Type', 'application/json')
        return ISerializeToJson(self.context)


@adapter(IDexterityContent, IAPIRequest)
class APIDexterityTraverser(DefaultPublishTraverse):

    def publishTraverse(self, request, name):
        self.request.response.setHeader('Content-Type', 'application/json')
        return ISerializeToJson(self.context)
