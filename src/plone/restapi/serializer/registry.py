from plone.registry.interfaces import IRegistry
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.types.interfaces import IJsonSchemaProvider
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IRequest
from zope.interface import Interface

class SerializeRegistryMixin:
    def serialize(self):
        batch = HypermediaBatch(self.request, list(self.records.keys()))
        results = {
            "@id": batch.canonical_url,
            "items_total": batch.items_total,
            "batching": batch.links if batch.links else {},
            "items": [
                self.make_item(key) for key in batch
            ]
        }
        return results

    def make_item(self, key):
        record = self.records[key]
        schema = getMultiAdapter(
            (record.field, record, self.request), IJsonSchemaProvider
        )
        return {
            "name": key,
            "value": self.records[key],
            "schema": {"properties": schema.get_schema()},
        }

@implementer(ISerializeToJson)
@adapter(IRegistry, IRequest, Interface)
class SerializeRegistryToJsonWithFilters(SerializeRegistryMixin):
    def __init__(self, registry, request, records):
        self.registry = registry
        self.request = request
        self.records = records
    def __call__(self):
        return self.serialize()


@implementer(ISerializeToJson)
@adapter(IRegistry, IRequest)
class SerializeRegistryToJson(SerializeRegistryMixin):
    def __init__(self, registry, request):
        self.registry = registry
        self.request = request
        self.records = registry.records

    def __call__(self):
        return self.serialize()
