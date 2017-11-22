# -*- coding: utf-8 -*-
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.ZCatalog.Lazy import Lazy
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface


BRAIN_METHODS = ['getPath', 'getURL']


@implementer(ISerializeToJson)
@adapter(ICatalogBrain, Interface)
class BrainSerializer(object):
    """Serializes a catalog brain to a Python data structure that can in turn
    be serialized to JSON.
    """

    def __init__(self, brain, request):
        self.brain = brain
        self.request = request

    def _get_metadata_to_include(self, metadata_fields):
        if metadata_fields and '_all' in metadata_fields:
            site = getSite()
            catalog = getToolByName(site, 'portal_catalog')
            metadata_attrs = catalog.schema() + BRAIN_METHODS
            return metadata_attrs

        return metadata_fields

    def __call__(self, metadata_fields=('_all',)):
        metadata_to_include = self._get_metadata_to_include(metadata_fields)

        # Start with a summary representation as our base
        result = getMultiAdapter(
            (self.brain, self.request), ISerializeToJsonSummary)()

        for attr in metadata_to_include:
            value = getattr(self.brain, attr, None)

            # Handle values that are provided via methods on brains, like
            # getPath or getURL (see ICatalogBrain for details)
            if attr in BRAIN_METHODS:
                value = value()

            value = json_compatible(value)

            # TODO: Deal with metadata attributes that already contain
            # timestamps as isoformat strings, like 'Created'
            result[attr] = value

        return result


@implementer(ISerializeToJson)
@adapter(Lazy, Interface)
class LazyCatalogResultSerializer(object):
    """Serializes a ZCatalog resultset (one of the subclasses of `Lazy`) to
    a Python data structure that can in turn be serialized to JSON.
    """

    def __init__(self, lazy_resultset, request):
        self.lazy_resultset = lazy_resultset
        self.request = request

    def __call__(self, metadata_fields=(), fullobjects=False):
        batch = HypermediaBatch(self.request, self.lazy_resultset)

        results = {}
        results['@id'] = batch.canonical_url
        results['items_total'] = batch.items_total
        if batch.links:
            results['batching'] = batch.links

        results['items'] = []
        for brain in batch:
            if fullobjects:
                result = getMultiAdapter(
                    (brain.getObject(), self.request), ISerializeToJson)(
                        include_items=False)
            else:
                result = getMultiAdapter(
                    (brain, self.request), ISerializeToJsonSummary)()

                # Merge additional metadata into the summary we already have
                if metadata_fields:
                    metadata = getMultiAdapter(
                        (brain, self.request),
                        ISerializeToJson)(metadata_fields=metadata_fields)
                    result.update(metadata)

            results['items'].append(result)

        return results
