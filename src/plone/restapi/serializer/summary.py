from plone.app.contentlisting.interfaces import IContentListingObject
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from plone.restapi.serializer.converters import json_compatible
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.component import getAllUtilitiesRegisteredFor


@implementer(IJSONSummarySerializerMetadata)
class JSONSummarySerializerMetadata:
    def default_metadata_fields(self):
        return {
            "@id",
            "@type",
            "description",
            "review_state",
            "title",
        }

    def field_accessors(self):
        return {
            "@id": "getURL",
            "@type": "PortalType",
            "description": "Description",
            "title": "Title",
        }

    def non_metadata_attributes(self):
        return {
            "getPath",
            "getURL",
        }

    def blocklisted_attributes(self):
        return {
            "getDataOrigin",
            "getObject",
            "getUserData",
        }


def merge_serializer_metadata_utilities_data():
    """Merge data returned by utilities registered for IJSONSummarySerializerMetadata."""
    serializer_metadata = {
        "default_metadata_fields": set(),
        "field_accessors": {},
        "non_metadata_attributes": set(),
        "blocklisted_attributes": set(),
    }
    utils = getAllUtilitiesRegisteredFor(IJSONSummarySerializerMetadata)
    for name in serializer_metadata.keys():
        for util in utils:
            method = getattr(util, name, None)
            if not method:
                continue
            value = method()
            serializer_metadata[name].update(value)
    return serializer_metadata


@implementer(ISerializeToJsonSummary)
@adapter(Interface, Interface)
class DefaultJSONSummarySerializer:
    """Default ISerializeToJsonSummary adapter.

    Requires context to be adaptable to IContentListingObject, which is
    the case for all content objects providing IContentish.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        # Cache summary_serializer_metadata on request
        metadata = self.request.form.get("summary_serializer_metadata", None)
        if not metadata:
            metadata = merge_serializer_metadata_utilities_data()
            self.request.set("summary_serializer_metadata", metadata)

        self.default_metadata_fields = metadata["default_metadata_fields"]
        self.field_accessors = metadata["field_accessors"]
        self.non_metadata_attributes = metadata["non_metadata_attributes"]
        self.blocklisted_attributes = metadata["blocklisted_attributes"]

    def __call__(self):
        obj = IContentListingObject(self.context)

        summary = {}
        for field in self.metadata_fields():
            if field.startswith("_") or field in self.blocklisted_attributes:
                continue
            accessor = self.field_accessors.get(field, field)
            value = getattr(obj, accessor, None)
            try:
                if callable(value):
                    value = value()
            except WorkflowException:
                summary[field] = None
                continue
            summary[field] = json_compatible(value)
        return summary

    def metadata_fields(self):
        query = self.request.form
        if not query:
            # maybe its a POST request
            query = json_body(self.request)
        additional_metadata_fields = query.get("metadata_fields", [])
        if not isinstance(additional_metadata_fields, list):
            additional_metadata_fields = [additional_metadata_fields]
        additional_metadata_fields = set(additional_metadata_fields)

        if "_all" in additional_metadata_fields:
            fields_cache = self.request.get("_summary_fields_cache", None)
            if fields_cache is None:
                catalog = getToolByName(self.context, "portal_catalog")
                fields_cache = set(catalog.schema()) | self.non_metadata_attributes
                self.request.set("_summary_fields_cache", fields_cache)
            additional_metadata_fields = fields_cache

        return self.default_metadata_fields | additional_metadata_fields


@implementer(ISerializeToJsonSummary)
@adapter(IPloneSiteRoot, Interface)
class SiteRootJSONSummarySerializer:
    """ISerializeToJsonSummary adapter for the Plone Site root."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        summary = json_compatible(
            {
                "@id": self.context.absolute_url(),
                "@type": self.context.portal_type,
                "title": self.context.title,
                "description": self.context.description,
            }
        )
        return summary
