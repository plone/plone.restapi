from AccessControl import getSecurityManager
from importlib import import_module
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.dexterity.utils import iterSchemata
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.blocks import apply_block_serialization_transforms
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.expansion import expandable_elements
from plone.restapi.services.locking import lock_info
from plone.supermodel.utils import mergedTaggedValueDict
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from zope.security.interfaces import IPermission

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
            "title": self.context.Title(),
            "parent": {},
            "is_folderish": True,
            "description": self.context.description,
        }

        if HAS_PLONE_6:
            # Insert Plone Site DX root field values
            for schema in iterSchemata(self.context):
                read_permissions = mergedTaggedValueDict(schema, READ_PERMISSIONS_KEY)

                for name, field in getFields(schema).items():

                    if not self.check_permission(
                        read_permissions.get(name), self.context
                    ):
                        continue

                    # serialize the field
                    serializer = queryMultiAdapter(
                        (field, self.context, self.request), IFieldSerializer
                    )
                    value = serializer()
                    result[json_compatible(name)] = value

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

        return result

    def check_permission(self, permission_name, obj):
        if permission_name is None:
            return True

        if permission_name not in self.permission_cache:
            permission = queryUtility(IPermission, name=permission_name)
            if permission is None:
                self.permission_cache[permission_name] = True
            else:
                sm = getSecurityManager()
                self.permission_cache[permission_name] = bool(
                    sm.checkPermission(permission.title, obj)
                )
        return self.permission_cache[permission_name]

    def serialize_blocks(self):
        # This is only for below 6
        blocks = json.loads(getattr(self.context, "blocks", "{}"))
        if not blocks:
            return blocks
        for id, block_value in blocks.items():
            blocks[id] = apply_block_serialization_transforms(block_value, self.context)
        return blocks
