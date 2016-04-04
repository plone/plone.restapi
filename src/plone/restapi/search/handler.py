# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
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

    def _constrain_query_by_path(self, query):
        # If no 'path' parameter was supplied, restrict search to current
        # context and its children by adding a path constraint
        if 'path' not in query:
            path = '/'.join(self.context.getPhysicalPath())
            query['path'] = path

    def search(self, query=None):
        if query is None:
            query = {}

        self._constrain_query_by_path(query)

        lazy_resultset = self.catalog.searchResults(query)
        results = getMultiAdapter((lazy_resultset, self.request),
                                  ISerializeToJson)()
        return results
