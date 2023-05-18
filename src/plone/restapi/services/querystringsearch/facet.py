from zope.component import getUtility
from Products.CMFCore.interfaces import ICatalogTool

from plone.restapi.utils import get_query, searchResults


class Facet:
    """Returns facet count."""

    def __init__(self, context, name, querybuilder_params):
        self.context = context
        self.name = name
        self.querybuilder_params = querybuilder_params

    def reply(self):
        facet_count = {}
        ctool = getUtility(ICatalogTool)

        query = self.querybuilder_params.get("query", None)

        try:
            index = ctool._catalog.getIndex(self.name)
        except:
            index = None

        if query:
            self.querybuilder_params["query"] = [
                qs for qs in query if qs["i"] != self.name
            ]

        brains_rids = set(
            searchResults(get_query(self.context, **self.querybuilder_params))
        )
        rids = brains_rids.intersection(index.documentToKeyMap())

        for rid in rids:
            for key in index.keyForDocument(rid):
                if key not in facet_count:
                    facet_count[key] = 0
                facet_count[key] += 1

        return {
            "facets": {
                self.name: {
                    "count": len(rids),
                    "data": [
                        {"value": key, "count": value}
                        for key, value in facet_count.items()
                    ],
                }
            }
            if self.name
            else {},
        }
