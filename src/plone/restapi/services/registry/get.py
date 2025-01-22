from plone.registry import Registry
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class RegistryGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@registry as parameters
        self.params.append(name)
        return self

    @property
    def _get_record_name(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (dotted name of"
                "the record to be retrieved)"
            )

        return self.params[0]

    def reply(self):
        registry = getUtility(IRegistry)
        if self.params:
            value = registry[self._get_record_name]
            return json_compatible(value)
        else:  # batched listing
            if q := self.request.form.get("q"):

                tmp_registry = Registry()
                for key in registry.records.keys():
                    if key.startswith(q):
                        tmp_registry.records[key] = registry.records[key]
                registry = tmp_registry
            serializer = getMultiAdapter(
                (registry, self.request),
                ISerializeToJson,
            )
            return serializer()
