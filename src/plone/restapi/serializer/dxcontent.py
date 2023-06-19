from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import boolean_value
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import IObjectPrimaryFieldTarget
from plone.restapi.interfaces import IPrimaryFieldTarget
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.expansion import expandable_elements
from plone.restapi.serializer.nextprev import NextPrevious
from plone.restapi.services.locking import lock_info
from plone.restapi.serializer.utils import get_portal_type_title
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.supermodel.utils import mergedTaggedValueDict
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from zope.security.interfaces import IPermission


try:
    # plone.app.iterate is by intend not part of Products.CMFPlone dependencies
    # so we can not rely on having it
    from plone.restapi.serializer.working_copy import WorkingCopyInfo
except ImportError:
    WorkingCopyInfo = None


@implementer(ISerializeToJson)
@adapter(IDexterityContent, Interface)
class SerializeToJson:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.metadata_fields = self.getParam("metadata_fields", list)
        self.include_basic_metadata = self.getParam(
            "include_basic_metadata", bool, True
        )
        self.include_expandable_elements = self.getParam(
            "include_expandable_elements", bool, True
        )

        self.permission_cache = {}

    def can_include_metadata(self, metadata):
        if self.include_basic_metadata:
            return True
        if metadata in self.metadata_fields:
            return True
        return False

    def getVersion(self, version):
        if version == "current":
            return self.context
        else:
            repo_tool = getToolByName(self.context, "portal_repository")
            return repo_tool.retrieve(self.context, int(version)).object

    def getParam(self, param, value_type, default_value=None):
        value = self.request.form.get(param, default_value)
        if value_type == list and not value:
            return []
        if value_type == list and type(value) != list:
            return [value]
        if value_type == bool:
            return boolean_value(value)
        return value

    def getId(self, obj):
        return obj.id

    def getTypeTitle(self, obj):
        return get_portal_type_title(obj.portal_type)

    def getUID(self, obj):
        return obj.UID()

    def getParent(self, obj):
        parent = aq_parent(aq_inner(obj))
        parent_summary = getMultiAdapter(
            (parent, self.request), ISerializeToJsonSummary
        )()
        return parent_summary

    def getCreated(self, obj):
        return json_compatible(obj.created())

    def getModified(self, obj):
        return json_compatible(obj.modified())

    def getLayout(self, **kwargs):
        return self.context.getLayout()

    def getLock(self, obj):
        return lock_info(obj)

    def getReviewState(self, obj):
        return self._get_workflow_state(obj)

    def getAllowDiscussion(self, **kwargs):
        return getMultiAdapter(
            (self.context, self.request), name="conversation_view"
        ).enabled()

    def getTargetUrl(self, **kwargs):
        target_url = getMultiAdapter(
            (self.context, self.request), IObjectPrimaryFieldTarget
        )()
        return target_url

    def __call__(self, version=None, include_items=True):
        version = "current" if version is None else version

        obj = self.getVersion(version)

        result = {
            "@id": obj.absolute_url(),
            "@type": obj.portal_type,
            "is_folderish": False,
        }
        metadatas = {
            # '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
            "id": self.getId,
            "type_title": self.getTypeTitle,
            "UID": self.getUID,
            "parent": self.getParent,
            "created": self.getCreated,
            "modified": self.getModified,
            "layout": self.getLayout,
            # Insert locking information
            "lock": self.getLock,
            "review_state": self.getReviewState,
            "allow_discussion": self.getAllowDiscussion,
            "targetUrl": self.getTargetUrl,
            "version": version,
        }

        # Filter basic metadata
        for key, value in metadatas.items():
            if not self.can_include_metadata(key):
                continue
            if callable(value):
                value = value(obj=obj)
            if value is not None:
                result[key] = value

        # Insert next/prev information
        if self.can_include_metadata("previous_item") or self.can_include_metadata(
            "next_item"
        ):
            try:
                nextprevious = NextPrevious(obj)
                result.update(
                    {
                        "previous_item": nextprevious.previous,
                        "next_item": nextprevious.next,
                    }
                )
            except ValueError:
                # If we're serializing an old version that was renamed or moved,
                # then its id might not be found inside the current object's container.
                result.update({"previous_item": {}, "next_item": {}})

        # Insert working copy information
        if self.can_include_metadata("working_copy"):
            if WorkingCopyInfo is not None:
                baseline, working_copy = WorkingCopyInfo(
                    self.context
                ).get_working_copy_info()
                result.update(
                    {
                        "working_copy": working_copy,
                        "working_copy_of": baseline,
                    }
                )

        # Insert expandable elements
        if self.include_expandable_elements:
            result.update(expandable_elements(self.context, self.request))

        # Insert field values
        for schema in iterSchemata(self.context):
            read_permissions = mergedTaggedValueDict(schema, READ_PERMISSIONS_KEY)

            for name, field in getFields(schema).items():
                if not self.can_include_metadata(name):
                    continue
                if not self.check_permission(read_permissions.get(name), obj):
                    continue

                # serialize the field
                serializer = queryMultiAdapter(
                    (field, obj, self.request), IFieldSerializer
                )
                value = serializer()
                result[json_compatible(name)] = value

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
        folder_metadata = super().__call__(version=version)

        folder_metadata.update({"is_folderish": True})
        result = folder_metadata

        include_items = self.request.form.get("include_items", include_items)
        include_items = boolean_value(include_items)
        if include_items:
            query = self._build_query()

            catalog = getToolByName(self.context, "portal_catalog")
            brains = catalog(query)

            batch = HypermediaBatch(self.request, brains)

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
class DexterityObjectPrimaryFieldTarget:
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
