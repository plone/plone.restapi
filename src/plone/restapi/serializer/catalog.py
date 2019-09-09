# -*- coding: utf-8 -*-
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from Products.ZCatalog.Lazy import Lazy
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(Lazy, Interface)
class LazyCatalogResultSerializer(object):
    """Serializes a ZCatalog resultset (one of the subclasses of `Lazy`) to
    a Python data structure that can in turn be serialized to JSON.
    """

    def __init__(self, lazy_resultset, request):
        self.lazy_resultset = lazy_resultset
        self.request = request

    def __call__(self, metadata_fields=(), fullobjects=False):
        batch = HypermediaBatch(self.request, self.lazy_resultset)

        results = {}
        results["@id"] = batch.canonical_url
        results["items_total"] = batch.items_total
        links = batch.links
        if links:
            results["batching"] = links

        results["items"] = []
        for brain in batch:
            if fullobjects:
                result = getMultiAdapter(
                    (brain.getObject(), self.request), ISerializeToJson
                )(include_items=False)
            else:
                result = getMultiAdapter(
                    (brain, self.request), ISerializeToJsonSummary
                )()

            results["items"].append(result)

        return results
