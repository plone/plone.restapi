from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.querystringsearch.get import QuerystringSearch
from Products.CMFCore.utils import getToolByName
import json


class FacetCountGet(Service):
    """Returns facet count."""

    def reply(self):
        facet_count = {}
        ctool = getToolByName(self.context, "portal_catalog")
        body = json_body(self.request)

        facet = body.get("facet", None)
        query = body.get("query", None)

        try:
            index = ctool._catalog.getIndex(facet)
        except:
            index = None

        if query:
            body["query"] = [qs for qs in query if qs["i"] != facet]
            self.request.set("BODY", json.dumps(body))

        brains = QuerystringSearch(self.context, self.request).getResults()

        brains_rids = set(brain.getRID() for brain in brains)
        index_rids = [rid for rid in index.documentToKeyMap()] if index else []

        rids = brains_rids.intersection(index_rids)

        for rid in rids:
            for key in index.keyForDocument(rid):
                if key not in facet_count:
                    facet_count[key] = 0
                facet_count[key] += 1

        return {
            "@id": "%s/@facet-count" % self.context.absolute_url(),
            "facets": {
                facet: {
                    "count": len(rids),
                    "data": [
                        {"value": key, "count": value}
                        for key, value in facet_count.items()
                    ],
                }
            }
            if facet
            else {},
        }
