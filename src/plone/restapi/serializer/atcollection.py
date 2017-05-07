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

    def __call__(self, version=None):
        collection_metadata = super(SerializeCollectionToJson, self).__call__(
            version=version,
        )
        results = self.context.results(batch=False)
        batch = HypermediaBatch(self.request, results)

        results = collection_metadata
        results['@id'] = batch.canonical_url
        results['items_total'] = batch.items_total
        if batch.links:
            results['batching'] = batch.links

        results['items'] = [
            getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
            for brain in batch
        ]
        return results
