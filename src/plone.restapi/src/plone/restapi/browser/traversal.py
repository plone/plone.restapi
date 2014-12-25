# -*- coding: utf-8 -*-
from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from plone.restapi.interfaces import IAPIRequest
from zope.interface import alsoProvides
from plone.dexterity.interfaces import IDexterityContent
from zope.component import adapter
from ZPublisher.BaseRequest import DefaultPublishTraverse
from Products.Five.browser import BrowserView
from plone.restapi.interfaces import ISerializeToJson


class ApiTraverse(SimpleItem):
    """Mark the @@json view with the IAPIRequest interface.
    """
    implements(IPublishTraverse)

    def publishTraverse(self, request, name):
        alsoProvides(self.request, IAPIRequest)
        return self.context


class JsonView(BrowserView):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        return ISerializeToJson(self.context)


@adapter(IDexterityContent, IAPIRequest)
class APIInnerTraverser(DefaultPublishTraverse):

    def publishTraverse(self, request, name):
        return JsonView(self.context, request)
        return super(APIInnerTraverser, self).publishTraverse(request, name)
