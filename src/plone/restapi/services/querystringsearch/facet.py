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
        self.querybuilder_parameters = querybuilder_parameters.copy()
        self.querybuilder_criteria_parameters = querybuilder_parameters.copy()
        self.querybuilder_parameters["query"] = [
            qs
            for qs in querybuilder_parameters.get("query", [])
            if qs["i"] != self.name or  ('criteria' in qs and qs["criteria"] is True)
        ]
        self.querybuilder_parameters["rids"] = True
        self.querybuilder_criteria_parameters["rids"] = True
        self.querybuilder_criteria_parameters["query"] =[
            qs
            for qs in querybuilder_parameters.get("query", [])
            if 'criteria' in qs and qs["criteria"] is True
        ]

    def getFacet(self):
        ctool = getUtility(ICatalogTool)
        count = {}
        count_criteria = {}
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
        querybuilder_criteria = getMultiAdapter(
            (self.context, self.request), name="querybuilderresults"
        )

        brains_rids = querybuilder(**self.querybuilder_parameters)
        brains_rids_criteria = querybuilder_criteria(**self.querybuilder_criteria_parameters)
        # Get the rids for the brains that have the facet index set to the value we are interested in
        rids = intersection(brains_rids, index.documentToKeyMap())
        rids_criteria = intersection(brains_rids_criteria, index.documentToKeyMap())
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
        for rid in rids_criteria:
            keys = index.keyForDocument(rid)
            if isinstance(keys, str):
                keys = [keys]
            if not isinstance(keys, list):
                continue
            for key in keys:
                if key not in count_criteria:
                    count_criteria[key] = 0
                count_criteria[key] += 1

        results = {
            "name": self.name,
            "count": len(rids),
            "data": {},
            "count_criteria":len(rids_criteria)
        }

        for key, value in count.items():
            if key in count_criteria and count_criteria[key] > 0:
                results["data"][key] = value

        for key,value in count_criteria.items():
                if key not in  results["data"]:
                  results["data"][key] = 0

        return results
