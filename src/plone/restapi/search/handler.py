# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import IZCatalogCompatibleQuery
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


class SearchHandler(object):
    """Executes a catalog search based on a query dict, and returns
    JSON compatible results.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.catalog = getToolByName(self.context, 'portal_catalog')

    def _parse_query(self, query):
        catalog_compatible_query = getMultiAdapter(
            (self.context, self.request), IZCatalogCompatibleQuery)(query)
        return catalog_compatible_query

    def _constrain_query_by_path(self, query):
        """If no 'path' query was supplied, restrict search to current
        context and its children by adding a path constraint.

        The following cases can happen here:
        - No 'path' parameter at all
        - 'path' query dict with options, but no actual 'query' inside
        - 'path' supplied as a string
        - 'path' supplied as a complete query dict
        """
        if 'path' not in query:
            query['path'] = {}

        if isinstance(query['path'], dict) and 'query' not in query['path']:
            # We either had no 'path' parameter at all, or an incomplete
            # 'path' query dict (with just ExtendedPathIndex options (like
            # 'depth'), but no actual path 'query' in it).
            #
            # In either case, we'll prefill with the context's path
            path = '/'.join(self.context.getPhysicalPath())
            query['path']['query'] = path

    def search(self, query=None):
        if query is None:
            query = {}
        if 'fullobjects' in query:
            fullobjects = True
            del query['fullobjects']
        else:
            fullobjects = False

        metadata_fields = query.pop('metadata_fields', [])
        if not isinstance(metadata_fields, list):
            metadata_fields = [metadata_fields]

        self._constrain_query_by_path(query)
        query = self._parse_query(query)

        lazy_resultset = self.catalog.searchResults(query)
        results = getMultiAdapter(
            (lazy_resultset, self.request),
            ISerializeToJson)(
                metadata_fields=metadata_fields, fullobjects=fullobjects)

        return results
