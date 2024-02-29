from BTrees.IIBTree import intersection
from Products.CMFCore.interfaces import ICatalogTool
from zope.component import getUtility
from zope.component import getMultiAdapter


class Facet:
    """Returns facet count."""

    def __init__(self, context, request, name, querybuilder_parameters):
        self.context = context
        self.request = request
        self.name = name
        self.querybuilder_parameters = querybuilder_parameters
        self.querybuilder_parameters["query"] = [
            qs
            for qs in querybuilder_parameters.get("query", [])
            if qs["i"] != self.name
        ]
        self.querybuilder_parameters["rids"] = True

    def getFacet(self):
        ctool = getUtility(ICatalogTool)
        count = {}
        index = None
        try:
            index = ctool._catalog.getIndex(self.name)
        finally:
            if index is None:
                return None
        # Get the brains for the query without the facet
        querybuilder = getMultiAdapter(
            (self.context, self.request), name="querybuilderresults"
        )
        brains_rids = querybuilder(**self.querybuilder_parameters)
        # Get the rids for the brains that have the facet index set to the value we are interested in
        rids = intersection(brains_rids, index.documentToKeyMap())

        for rid in rids:
            keys = index.keyForDocument(rid)
            if isinstance(keys, str):
                keys = [keys]
            if not isinstance(keys, list):
                continue
            for key in keys:
                if key not in count:
                    count[key] = 0
                count[key] += 1

        results = {
            "name": self.name,
            "count": len(rids),
            "data": {},
        }

        for key, value in count.items():
            results["data"][key] = value

        return results
