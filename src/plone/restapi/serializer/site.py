from importlib import import_module
from plone.restapi.batching import HypermediaBatch
from plone.restapi.bbb import IPloneSiteRoot
from plone.restapi.blocks import iter_block_transform_handlers
from plone.restapi.blocks import visit_blocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.dxcontent import get_allow_discussion_value
from plone.restapi.serializer.expansion import expandable_elements
from plone.restapi.serializer.utils import get_portal_type_title, serialize_schemas
from plone.restapi.services.locking import lock_info
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

import json


HAS_PLONE_6 = getattr(
    import_module("Products.CMFPlone.factory"), "PLONE60MARKER", False
)


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
            "@id": self.context.absolute_url(),
            "id": self.context.id,
            "@type": "Plone Site",
            "type_title": get_portal_type_title("Plone Site"),
            "title": self.context.Title(),
            "parent": {},
            "is_folderish": True,
            "description": self.context.description,
        }

        if HAS_PLONE_6:
            result["UID"] = self.context.UID()
            # Insert review_state
            wf = getToolByName(self.context, "portal_workflow")
            result["review_state"] = wf.getInfoFor(
                ob=self.context, name="review_state", default=None
            )

            # Insert Plone Site DX root field values
            result.update(serialize_schemas(self.context, self.request))

            # Insert locking information
            result.update({"lock": lock_info(self.context)})
        else:
            # Apply the fake blocks behavior in site root hack using site root properties
            result.update(
                {
                    "blocks": self.serialize_blocks(),
                    "blocks_layout": json.loads(
                        getattr(self.context, "blocks_layout", "{}")
                    ),
                }
            )

        # Insert expandable elements
        result.update(expandable_elements(self.context, self.request))

        result["items_total"] = batch.items_total
        if batch.links:
            result["batching"] = batch.links

        result["items"] = [
            getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
            for brain in batch
        ]

        get_allow_discussion_value(self.context, self.request, result)

        return result

    def serialize_blocks(self):
        # This is only for below 6
        blocks = json.loads(getattr(self.context, "blocks", "{}"))
        for block in visit_blocks(self.context, blocks):
            new_block = block.copy()
            for handler in iter_block_transform_handlers(
                self.context, block, IBlockFieldSerializationTransformer
            ):
                new_block = handler(new_block)
            block.clear()
            block.update(new_block)
        return blocks
