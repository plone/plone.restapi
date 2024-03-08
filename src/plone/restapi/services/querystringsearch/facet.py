from BTrees.IIBTree import intersection
from Products.CMFCore.interfaces import ICatalogTool
from zope.component import getUtility
from zope.component import getMultiAdapter
from pkg_resources import get_distribution
from pkg_resources import parse_version

zcatalog_version = get_distribution("Products.ZCatalog").version
if parse_version(zcatalog_version) >= parse_version("5.1"):
    SUPPORT_NOT_UUID_QUERIES = True
else:
    SUPPORT_NOT_UUID_QUERIES = False

class Facet:
    """Returns facet count."""

    def __init__(
        self, context, request, name, querybuilder_parameters, brains_rids_mandatory
    ):

        self.context = context
        self.request = request
        self.name = name
        self.querybuilder_parameters = querybuilder_parameters.copy()
        self.querybuilder_mandatory_parameters = querybuilder_parameters.copy()
        self.querybuilder_parameters["query"] = [
            qs
            for qs in querybuilder_parameters.get("query", [])
            if qs["i"] != self.name or ("mandatory" in qs and qs["mandatory"] is True)
        ]
        self.querybuilder_parameters["rids"] = True
        self.querybuilder_mandatory_parameters["rids"] = True
        self.querybuilder_mandatory_parameters["query"] = [
            qs
            for qs in querybuilder_parameters.get("query", [])
            if "mandatory" in qs and qs["mandatory"] is True
        ]
        self.brain_rids_mandatory = brains_rids_mandatory
        if SUPPORT_NOT_UUID_QUERIES:
            self.querybuilder_parameters.update(
                dict(custom_query={"UID": {"not": self.context.UID()}})
            )


    def getFacet(self):
        ctool = getUtility(ICatalogTool)
        count = {}
        count_mandatory = {}
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
        brains_rids_mandatory = self.brain_rids_mandatory
        # Get the rids for the brains that have the facet index set to the value we are interested in
        index_rids = index.documentToKeyMap()
        rids = intersection(brains_rids, index_rids)
        rids_mandatory = intersection(brains_rids_mandatory, index_rids)

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
        for rid in rids_mandatory:
            keys = index.keyForDocument(rid)
            if isinstance(keys, str):
                keys = [keys]
            if not isinstance(keys, list):
                continue
            for key in keys:
                if key not in count_mandatory:
                    count_mandatory[key] = 0
                count_mandatory[key] += 1

        results = {
            "name": self.name,
            "count": len(rids),
            "data": {},
        }

        for key, _ in count_mandatory.items():
            results["data"][key] = count[key] if key in count else 0 

        return results
