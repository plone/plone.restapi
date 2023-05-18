from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
import json

from plone.restapi.utils import get_query, searchResults


class FacetCount(Service):
    """Returns facet count."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def reply(self):
        facet_count = {}
        ctool = getToolByName(self.context, "portal_catalog")
        body = json_body(self.request)

        body["b_start"] = int(body.get("b_start", 0))
        body["b_size"] = int(body.get("b_size", 25))
        body["limit"] = int(body.get("limit", 1000))
        body["rids"] = True

        facet = body.get("facet", None)
        query = body.get("query", None)

        try:
            index = ctool._catalog.getIndex(facet)
        except:
            index = None

        if query:
            body["query"] = [qs for qs in query if qs["i"] != facet]
            self.request.set("BODY", json.dumps(body))

        brains_rids = set(searchResults(get_query(self.context, **body)))
        rids = brains_rids.intersection(index.documentToKeyMap())

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
    
