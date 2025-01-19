from plone.registry.interfaces import IRegistry
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.types.interfaces import IJsonSchemaProvider
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IRequest
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IRegistry, IRequest, Interface)
class SerializeRegistryToJson:
    def __init__(self, registry, request, records=None):
        self.registry = registry
        self.request = request
        self.records = records or registry.records

    def __call__(self):
        batch = HypermediaBatch(self.request, list(self.records.keys()))

        results = {}
        results["@id"] = batch.canonical_url
        results["items_total"] = batch.items_total
        if batch.links:
            results["batching"] = batch.links

        def make_item(key):
            record = self.records[key]
            schema = getMultiAdapter(
                (record.field, record, self.request), IJsonSchemaProvider
            )
            data = {"name": key, "value": self.registry[key]}
            __traceback_info__ = (record, record.field, schema)
            data["schema"] = {"properties": schema.get_schema()}
            return data

        results["items"] = [make_item(key) for key in batch]
        return results
