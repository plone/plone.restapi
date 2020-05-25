# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFPlone.utils import base_hasattr
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import boolean_value
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import IPrimaryFieldTarget
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.interfaces import IObjectPrimaryFieldTarget
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.expansion import expandable_elements
from plone.restapi.serializer.nextprev import NextPrevious
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.supermodel.utils import mergedTaggedValueDict
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from zope.security.interfaces import IPermission


@implementer(ISerializeToJson)
@adapter(IDexterityContent, Interface)
class SerializeToJson(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.permission_cache = {}

    def getVersion(self, version):
        if version == "current":
            return self.context
        else:
            repo_tool = getToolByName(self.context, "portal_repository")
            return repo_tool.retrieve(self.context, int(version)).object

    def __call__(self, version=None, include_items=True):
        version = "current" if version is None else version

        obj = self.getVersion(version)
        parent = aq_parent(aq_inner(obj))
        parent_summary = getMultiAdapter(
            (parent, self.request), ISerializeToJsonSummary
        )()
        result = {
            # '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            "@id": obj.absolute_url(),
            "id": obj.id,
            "@type": obj.portal_type,
            "parent": parent_summary,
            "created": json_compatible(obj.created()),
            "modified": json_compatible(obj.modified()),
            "review_state": self._get_workflow_state(obj),
            "UID": obj.UID(),
            "version": version,
            "layout": self.context.getLayout(),
            "is_folderish": False,
        }

        # Insert next/prev information
        nextprevious = NextPrevious(obj)
        result.update(
            {"previous_item": nextprevious.previous, "next_item": nextprevious.next}
        )

        # Insert expandable elements
        result.update(expandable_elements(self.context, self.request))

        # Insert field values
        for schema in iterSchemata(self.context):
            read_permissions = mergedTaggedValueDict(schema, READ_PERMISSIONS_KEY)

            for name, field in getFields(schema).items():

                if not self.check_permission(read_permissions.get(name), obj):
                    continue

                # serialize the field
                serializer = queryMultiAdapter(
                    (field, obj, self.request), IFieldSerializer
                )
                value = serializer()
                result[json_compatible(name)] = value

        target_url = getMultiAdapter(
            (self.context, self.request), IObjectPrimaryFieldTarget
        )()
        if target_url:
            result["targetUrl"] = target_url

        result["allow_discussion"] = getMultiAdapter(
            (self.context, self.request), name="conversation_view"
        ).enabled()

        return result

    def _get_workflow_state(self, obj):
        wftool = getToolByName(self.context, "portal_workflow")
        review_state = wftool.getInfoFor(ob=obj, name="review_state", default=None)
        return review_state

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


@implementer(ISerializeToJson)
@adapter(IDexterityContainer, Interface)
class SerializeFolderToJson(SerializeToJson):
    def _build_query(self):
        path = "/".join(self.context.getPhysicalPath())
        query = {
            "path": {"depth": 1, "query": path},
            "sort_on": "getObjPositionInParent",
        }
        return query

    def __call__(self, version=None, include_items=True):
        folder_metadata = super(SerializeFolderToJson, self).__call__(version=version)

        folder_metadata.update({"is_folderish": True})
        result = folder_metadata

        include_items = self.request.form.get("include_items", include_items)
        include_items = boolean_value(include_items)
        if include_items:
            query = self._build_query()

            catalog = getToolByName(self.context, "portal_catalog")
            brains = catalog(query)

            batch = HypermediaBatch(self.request, brains)

            if "fullobjects" not in self.request.form:
                result["@id"] = batch.canonical_url
            result["items_total"] = batch.items_total
            if batch.links:
                result["batching"] = batch.links

            if "fullobjects" in list(self.request.form):
                result["items"] = getMultiAdapter(
                    (brains, self.request), ISerializeToJson
                )(fullobjects=True)["items"]
            else:
                result["items"] = [
                    getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
                    for brain in batch
                ]
        return result


@adapter(IDexterityContent, Interface)
@implementer(IObjectPrimaryFieldTarget)
class DexterityObjectPrimaryFieldTarget(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.permission_cache = {}

    def __call__(self):
        primary_field_name = self.get_primary_field_name()
        for schema in iterSchemata(self.context):
            read_permissions = mergedTaggedValueDict(schema, READ_PERMISSIONS_KEY)

            for name, field in getFields(schema).items():

                if not self.check_permission(read_permissions.get(name), self.context):
                    continue

                if name != primary_field_name:
                    continue

                target_adapter = queryMultiAdapter(
                    (field, self.context, self.request), IPrimaryFieldTarget
                )
                if target_adapter:
                    target = target_adapter()
                    if target:
                        return target

    def get_primary_field_name(self):
        fieldname = None
        info = None
        try:
            info = IPrimaryFieldInfo(self.context, None)
        except TypeError:
            # No primary field present
            pass
        if info is not None:
            fieldname = info.fieldname
        elif base_hasattr(self.context, "getPrimaryField"):
            field = self.context.getPrimaryField()
            fieldname = field.getName()
        return fieldname

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
