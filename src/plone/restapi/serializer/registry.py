# -*- coding: utf-8 -*-
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces import IRequest


@implementer(ISerializeToJson)
@adapter(IRegistry, IRequest)
class SerializeRegistryToJson(object):

    def __init__(self, registry, request):
        self.registry = registry
        self.request = request

    def __call__(self):
        records = self.registry.records
        # Batch keys, because that is a simple BTree
        batch = HypermediaBatch(self.request, records.keys())

        results = {}
        results['@id'] = batch.canonical_url
        results['items_total'] = batch.items_total
        if batch.links:
            results['batching'] = batch.links

        items = [{'name': key, 'value': self.registry[key]} for key in batch]
        results['items'] = items
        return results
