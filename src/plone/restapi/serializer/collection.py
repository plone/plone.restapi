# -*- coding: utf-8 -*-
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.contenttypes.interfaces import ICollection
from plone.restapi.interfaces import IContentListingSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(ICollection, Interface)
class SerializeCollectionToJson(SerializeToJson):

    def __call__(self):
        result = super(SerializeCollectionToJson, self).__call__()

        # XXX: collection.results() claims to return an IContentListing
        # based result, but it doesn't. It returns a Batch object.
        # -> Need to traverse to the @@contentlisting view for now for
        # Plone 5, or fall back to accessing Batch._sequence for Plone 4.
        try:
            members = self.context.restrictedTraverse('@@contentlisting')()
        except AttributeError:
            batch = self.context.results()
            members = batch._sequence

        result['member'] = getMultiAdapter(
            (IContentListing(members), self.request),
            IContentListingSerializer)()

        return result
