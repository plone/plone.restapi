# -*- coding: utf-8 -*-
from OFS.SimpleItem import SimpleItem
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser import BrowserView
from ZPublisher.BaseRequest import DefaultPublishTraverse

from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IAPIRequest
from plone.restapi.interfaces import ISerializeToJson

from zope.component import adapter
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


def mark_as_api_request(context, event):
    """Mark views with application/json as Content-Type with the IAPIRequest
       interface.
    """
    if event.request.getHeader('Content-Type') == 'application/json':
        alsoProvides(event.request, IAPIRequest)


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


@adapter(IDexterityContent, IAPIRequest)
class APIDexterityTraverser(DefaultPublishTraverse):

    def publishTraverse(self, request, name):
        return SerializeToJsonView(self.context, request)


@adapter(IPloneSiteRoot, IAPIRequest)
class APISiteRootTraverser(DefaultPublishTraverse):

    def publishTraverse(self, request, name):
        # Traversal in Plone always starts with the site root. Therefore we
        # have to guess if this is a real request for the portal root. What
        # Plone does on portal root is pretty complex, therefore we have to
        # check for multiple different scenarios. It would be good if this
        # could be refactored to be simpler and more reliable.

        # If we are at the default page, return the site root
        if self.context.getDefaultPage() == name:
            return SerializeToJsonView(self.context, request)

        # Traversal returns folder_listing on the site root
        if name == '' or name == 'folder_listing':
            return SerializeToJsonView(self.context, request)

        # If this is just the first traversal step, make sure the traversal
        # continues, so the APIDexterityTraverser is reached.
        return DefaultPublishTraverse.publishTraverse(self, request, name)
