# -*- coding: utf-8 -*-
from plone.app.collection.interfaces import ICollection
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.atcontent import SerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(ICollection, Interface)
class SerializeCollectionToJson(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        collection_metadata = super(SerializeCollectionToJson, self).__call__(
            version=version
        )
        brains = self.context.results(batch=False)
        batch = HypermediaBatch(self.request, brains)

        results = collection_metadata
        if not self.request.form.get("fullobjects"):
            results["@id"] = batch.canonical_url
        results["items_total"] = batch.items_total
        if batch.links:
            results["batching"] = batch.links

        if "fullobjects" in list(self.request.form):
            results["items"] = [
                getMultiAdapter((brain.getObject(), self.request), ISerializeToJson)()
                for brain in batch
            ]
        else:
            results["items"] = [
                getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
                for brain in batch
            ]
        return results
