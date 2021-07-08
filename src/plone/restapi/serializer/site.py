from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.expansion import expandable_elements
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import subscribers
from zope.interface import implementer
from zope.interface import Interface

import json


@implementer(ISerializeToJson)
@adapter(IPloneSiteRoot, Interface)
class SerializeSiteRootToJson:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _build_query(self):
        path = "/".join(self.context.getPhysicalPath())
        query = {
            "path": {"depth": 1, "query": path},
            "sort_on": "getObjPositionInParent",
        }
        return query

    def __call__(self, version=None):
        version = "current" if version is None else version
        if version != "current":
            return {}

        query = self._build_query()

        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(query)

        batch = HypermediaBatch(self.request, brains)

        result = {
            # '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            "@id": batch.canonical_url,
            "id": self.context.id,
            "@type": "Plone Site",
            "title": self.context.Title(),
            "parent": {},
            "is_folderish": True,
            "description": self.context.description,
            "blocks": self.serialize_blocks(),
            "blocks_layout": json.loads(
                getattr(self.context, "blocks_layout", "{}")
            ),  # noqa
        }

        # Insert expandable elements
        result.update(expandable_elements(self.context, self.request))

        result["items_total"] = batch.items_total
        if batch.links:
            result["batching"] = batch.links

        result["items"] = [
            getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
            for brain in batch
        ]

        return result

    def serialize_blocks(self):
        blocks = json.loads(getattr(self.context, "blocks", "{}"))
        if not blocks:
            return blocks
        for id, block_value in blocks.items():
            block_type = block_value.get("@type", "")
            handlers = []
            for h in subscribers(
                (self.context, self.request), IBlockFieldSerializationTransformer
            ):
                if h.block_type == block_type or h.block_type is None:
                    handlers.append(h)

            for handler in sorted(handlers, key=lambda h: h.order):
                if not getattr(handler, "disabled", False):
                    block_value = handler(block_value)

            blocks[id] = block_value
        return blocks
