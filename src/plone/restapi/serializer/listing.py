# -*- coding: utf-8 -*-
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.restapi.interfaces import IContentListingObjectSerializer
from plone.restapi.interfaces import IContentListingSerializer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IContentListingSerializer)
@adapter(IContentListing, Interface)
class ContentListingSerializer(object):

    def __init__(self, listing, request):
        self.listing = listing
        self.request = request

    def __call__(self):
        result = []
        for listing_obj in self.listing:
            entry = getMultiAdapter(
                (listing_obj, self.request),
                IContentListingObjectSerializer)()
            result.append(entry)

        return result


@implementer(IContentListingObjectSerializer)
@adapter(IContentListingObject, Interface)
class ContentListingObjectSerializer(object):

    def __init__(self, listing_obj, request):
        self.listing_obj = listing_obj
        self.request = request

    def __call__(self):
        entry = {
            '@id': self.listing_obj.getURL(),
            'title': self.listing_obj.Title(),
            'description': self.listing_obj.Description(),
        }
        return entry
