# -*- coding: utf-8 -*-
from OFS.SimpleItem import SimpleItem
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
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


class SerializeToJsonView(BrowserView):

    def __call__(self):
        # The json response needs to be wrapped in a browser view to have
        # access to context and request.
        self.request.response.setHeader('Content-Type', 'application/json')
        return ISerializeToJson(self.context)


@adapter(IPloneSiteRoot, IAPIRequest)
class APISiteRootTraverser(DefaultPublishTraverse):

    def publishTraverse(self, request, name):
        return SerializeToJsonView(self.context, request)


@adapter(IDexterityContent, IAPIRequest)
class APIDexterityTraverser(DefaultPublishTraverse):

    def publishTraverse(self, request, name):
        return SerializeToJsonView(self.context, request)
