from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.contenttypes.interfaces import ILink
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.dexterity.interfaces import IDexterityContainer
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.restapi.batching import HypermediaBatch
from plone.restapi.bbb import base_hasattr
from plone.restapi.deserializer import boolean_value
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import IObjectPrimaryFieldTarget
from plone.restapi.interfaces import IPrimaryFieldTarget
from plone.restapi.interfaces import ISchemaSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.expansion import expandable_elements
from plone.restapi.serializer.nextprev import NextPrevious
from plone.restapi.serializer.schema import _check_permission
from plone.restapi.serializer.utils import get_portal_type_title
from plone.restapi.services.locking import lock_info
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.supermodel.utils import mergedTaggedValueDict
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields


try:
    # plone.app.iterate is by intend not part of Products.CMFPlone dependencies
    # so we can not rely on having it
    from plone.restapi.serializer.working_copy import WorkingCopyInfo
except ImportError:
    WorkingCopyInfo = None


def update_with_working_copy_info(context, result):
    if WorkingCopyInfo is None:
        return

    working_copy_info = WorkingCopyInfo(context)
    try:
        baseline, working_copy = working_copy_info.get_working_copy_info()
    except TypeError:
        # not supported for this content type
        return
    result.update({"working_copy": working_copy, "working_copy_of": baseline})


def get_allow_discussion_value(context, request, result):
    # This test is to handle the situation of plone.app.discussion not being installed
    # or not being activated.
    if "allow_discussion" in result and IContentish.providedBy(context):
        try:
            view = getMultiAdapter((context, request), name="conversation_view")
            result["allow_discussion"] = view.enabled()
            return
        except ComponentLookupError:
            pass
    result["allow_discussion"] = False


@implementer(ISerializeToJson)
@adapter(IDexterityContent, Interface)
class SerializeToJson:
    def __init__(self, context, request):
        self.context = context
        self.request = request

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
            "type_title": get_portal_type_title(obj.portal_type),
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
        try:
            nextprevious = NextPrevious(obj)
            result.update(
                {"previous_item": nextprevious.previous, "next_item": nextprevious.next}
            )
        except ValueError:
            # If we're serializing an old version that was renamed or moved,
            # then its id might not be found inside the current object's container.
            result.update({"previous_item": {}, "next_item": {}})

        # Insert working copy information
        update_with_working_copy_info(self.context, result)

        # Insert locking information
        result.update({"lock": lock_info(obj)})

        # Insert expandable elements
        result.update(expandable_elements(self.context, self.request))

        # Insert field values
        for schema in iterSchemata(self.context):
            schema_serializer = getMultiAdapter(
                (schema, obj, self.request), ISchemaSerializer
            )
            result.update(schema_serializer())

        target_url = getMultiAdapter(
            (self.context, self.request), IObjectPrimaryFieldTarget
        )()
        if target_url:
            result["targetUrl"] = target_url

        get_allow_discussion_value(self.context, self.request, result)

        return result

    def _get_workflow_state(self, obj):
        wftool = getToolByName(self.context, "portal_workflow")
        review_state = wftool.getInfoFor(ob=obj, name="review_state", default=None)
        return review_state

    def check_permission(self, permission_name, obj):
        # Here for backwards-compatibility
        return _check_permission(permission_name, self, obj)


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

    def __call__(self):
        primary_field_name = self.get_primary_field_name()
        if not primary_field_name:
            return
        for schema in iterSchemata(self.context):
            read_permissions = mergedTaggedValueDict(schema, READ_PERMISSIONS_KEY)

            field = getFields(schema).get(primary_field_name)
            if field is None:
                continue
            if not self.check_permission(
                read_permissions.get(primary_field_name),
                self.context,
            ):
                return

            target_adapter = queryMultiAdapter(
                (field, self.context, self.request), IPrimaryFieldTarget
            )
            if not target_adapter:
                return
            return target_adapter()

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
        # for backwards-compatibility
        return _check_permission(permission_name, self, obj)


@adapter(ILink, Interface)
@implementer(IObjectPrimaryFieldTarget)
class LinkObjectPrimaryFieldTarget:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """
        If user can edit Link object, do not return remoteUrl
        """
        pm = getToolByName(self.context, "portal_membership")
        if bool(pm.isAnonymousUser()):
            for schema in iterSchemata(self.context):
                for name, field in getFields(schema).items():
                    if name == "remoteUrl":
                        serializer = queryMultiAdapter(
                            (field, self.context, self.request), IFieldSerializer
                        )
                        return serializer()
