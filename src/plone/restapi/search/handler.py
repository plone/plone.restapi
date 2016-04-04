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

    def search(self, query=None):
        if query is None:
            query = {}

        lazy_resultset = self.catalog.searchResults(query)
        results = getMultiAdapter((lazy_resultset, self.request),
                                  ISerializeToJson)()
        return results
