from pkg_resources import get_distribution
from pkg_resources import parse_version
from plone.restapi.bbb import IPloneSiteRoot
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from urllib import parse
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from plone.restapi.services.querystringsearch.facet import Facet


zcatalog_version = get_distribution("Products.ZCatalog").version
if parse_version(zcatalog_version) >= parse_version("5.1"):
    SUPPORT_NOT_UUID_QUERIES = True
else:
    SUPPORT_NOT_UUID_QUERIES = False


class QuerystringSearch:
    """Returns the querystring search results given a p.a.querystring data."""

    def __init__(self, context, request, params):
        self.context = context
        self.request = request
        self.params = params

    def __call__(self):
        self.setQuerybuilderParams()
        querybuilder_mandatory_parameters = self.querybuilder_parameters.copy()
        querybuilder_mandatory_parameters["query"] = [
            qs
            for qs in self.querybuilder_parameters.get("query", [])
            if "mandatory" in qs and qs["mandatory"] is True
        ]
        querybuilder_mandatory_parameters["rids"] = True

        # make serch work also on Plone Root
        if SUPPORT_NOT_UUID_QUERIES:
            querybuilder_mandatory_parameters.update(
                dict(custom_query={"UID": {"not": self.context.UID()}})
            )
        querybuilder = getMultiAdapter(
            (self.context, self.request), name="querybuilderresults"
        )

        brains_rids_mandatory = querybuilder(**querybuilder_mandatory_parameters)

        if len(self.params) > 0:
            results = Facet(
                self.context,
                self.request,
                name=self.params[0],
                querybuilder_parameters=self.querybuilder_parameters,
                brains_rids_mandatory=brains_rids_mandatory,
            ).getFacet()
            if results is None:
                raise BadRequest("Invalid facet")
            results["@id"] = (
                "%s/@querystring-search/%s"
                % (self.context.absolute_url(), self.params[0]),
            )
        else:
            results = self.getResults()
            results = getMultiAdapter((results, self.request), ISerializeToJson)(
                fullobjects=self.fullobjects
            )
            results["facets_count"] = {}
            for facet in self.facets:
                facet_results = Facet(
                    self.context,
                    self.request,
                    name=facet,
                    querybuilder_parameters=self.querybuilder_parameters,
                    brains_rids_mandatory=brains_rids_mandatory,
                ).getFacet()
                if facet_results:
                    results["facets_count"][facet] = facet_results
        return results

    def setQuerybuilderParams(self):
        try:
            data = json_body(self.request)
        except DeserializationError as err:
            raise BadRequest(str(err))

        query = data.get("query", None)
        try:
            b_start = int(data.get("b_start", 0))
        except ValueError:
            raise BadRequest("Invalid b_start")
        try:
            b_size = int(data.get("b_size", 25))
        except ValueError:
            raise BadRequest("Invalid b_size")
        sort_on = data.get("sort_on", None)
        sort_order = data.get("sort_order", None)
        try:
            limit = int(data.get("limit", 1000))
        except ValueError:
            raise BadRequest("Invalid limit")

        self.fullobjects = bool(data.get("fullobjects", False))
        self.facets = data.get("facets", [])

        if not query:
            raise BadRequest("No query supplied")

        if sort_order:
            sort_order = "descending" if sort_order == "descending" else "ascending"

        self.querybuilder_parameters = dict(
            query=query,
            brains=True,
            b_start=b_start,
            b_size=b_size,
            sort_on=sort_on,
            sort_order=sort_order,
            limit=limit,
        )

        if not IPloneSiteRoot.providedBy(self.context) and SUPPORT_NOT_UUID_QUERIES:
            self.querybuilder_parameters.update(
                dict(custom_query={"UID": {"not": self.context.UID()}})
            )

    def getResults(self):
        querybuilder = getMultiAdapter(
            (self.context, self.request), name="querybuilderresults"
        )
        return querybuilder(**self.querybuilder_parameters)


@implementer(IPublishTraverse)
class QuerystringSearchPost(Service):
    """Returns the querystring search results given a p.a.querystring data."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        querystring_search = QuerystringSearch(self.context, self.request, self.params)
        return querystring_search()


@implementer(IPublishTraverse)
class QuerystringSearchGet(Service):
    """Returns the querystring search results given a p.a.querystring data."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        # We need to copy the JSON query parameters from the querystring
        # into the request body, because that's where other code expects to find them
        self.request["BODY"] = parse.unquote(
            self.request.form.get("query", "{}")
        ).encode(self.request.charset)

        # unset the get parameters
        self.request.form = {}
        querystring_search = QuerystringSearch(self.context, self.request, self.params)
        return querystring_search()
