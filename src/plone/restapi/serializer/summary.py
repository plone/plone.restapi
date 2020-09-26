# -*- coding: utf-8 -*-
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

# fmt: off
DEFAULT_METADATA_FIELDS = set([
    '@id',
    '@type',
    'description',
    'review_state',
    'title',
])

FIELD_ACCESSORS = {
    "@id": "getURL",
    "@type": "PortalType",
    "description": "Description",
    "title": "Title",
}

NON_METADATA_ATTRIBUTES = set([
    "getPath",
    "getURL",
])

BLACKLISTED_ATTRIBUTES = set([
    'getDataOrigin',
    'getObject',
    'getUserData',
])
# fmt: on


@implementer(ISerializeToJsonSummary)
@adapter(Interface, Interface)
class DefaultJSONSummarySerializer(object):
    """Default ISerializeToJsonSummary adapter.

    Requires context to be adaptable to IContentListingObject, which is
    the case for all content objects providing IContentish.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        obj = IContentListingObject(self.context)

        summary = {}
        for field in self.metadata_fields():
            if field.startswith("_") or field in BLACKLISTED_ATTRIBUTES:
                continue
            accessor = FIELD_ACCESSORS.get(field, field)
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
        additional_metadata_fields = self.request.form.get("metadata_fields", [])
        if not isinstance(additional_metadata_fields, list):
            additional_metadata_fields = [additional_metadata_fields]
        additional_metadata_fields = set(additional_metadata_fields)

        if "_all" in additional_metadata_fields:
            fields_cache = self.request.get("_summary_fields_cache", None)
            if fields_cache is None:
                catalog = getToolByName(self.context, "portal_catalog")
                fields_cache = set(catalog.schema()) | NON_METADATA_ATTRIBUTES
                self.request.set("_summary_fields_cache", fields_cache)
            additional_metadata_fields = fields_cache

        return DEFAULT_METADATA_FIELDS | additional_metadata_fields


@implementer(ISerializeToJsonSummary)
@adapter(IPloneSiteRoot, Interface)
class SiteRootJSONSummarySerializer(object):
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
