# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import boolean_value
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.expansion import expandable_elements
from plone.restapi.serializer.nextprev import NextPrevious
from Products.Archetypes.interfaces import IBaseFolder
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IBaseObject, Interface)
class SerializeToJson(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getVersion(self, version):
        if version == "current":
            return self.context
        else:
            repo_tool = getToolByName(self.context, "portal_repository")
            return repo_tool.retrieve(self.context, int(version)).object

    def __call__(self, version=None, include_items=False):
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
            "review_state": self._get_workflow_state(obj),
            "UID": obj.UID(),
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

        for field in obj.Schema().fields():

            if "r" not in field.mode or not field.checkPermission(
                "r", obj
            ):  # noqa: E501
                continue

            name = field.getName()

            serializer = queryMultiAdapter(
                (field, self.context, self.request), IFieldSerializer
            )
            if serializer is not None:
                result[name] = serializer()

        return result

    def _get_workflow_state(self, obj):
        wftool = getToolByName(self.context, "portal_workflow")
        review_state = wftool.getInfoFor(ob=obj, name="review_state", default=None)
        return review_state


@implementer(ISerializeToJson)
@adapter(IBaseFolder, Interface)
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
