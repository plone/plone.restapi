# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.types.interfaces import IJsonSchemaProvider
from zope.component import adapter
from zope.component import getMultiAdapter
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
        batch = HypermediaBatch(self.request, list(records))

        results = {}
        results["@id"] = batch.canonical_url
        results["items_total"] = batch.items_total
        if batch.links:
            results["batching"] = batch.links

        def make_item(key):
            record = records[key]
            schema = getMultiAdapter(
                (record.field, record, self.request), IJsonSchemaProvider
            )
            data = {"name": key, "value": self.registry[key]}
            __traceback_info__ = (record, record.field, schema)
            data["schema"] = {"properties": schema.get_schema()}
            return data

        results["items"] = [make_item(key) for key in batch]
        return results
