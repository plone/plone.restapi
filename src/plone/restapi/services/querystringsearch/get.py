from pkg_resources import get_distribution
from pkg_resources import parse_version
from plone.restapi.bbb import IPloneSiteRoot
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from urllib import parse
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
        data = json_body(self.request)
        fullobjects = data.get("fullobjects", False)

        self.setQuerybuilderParams()

        if len(self.params) > 0:
            results = Facet(
                self.context,
                name=self.params[0],
                querybuilder_params=self.querybuilder_params,
            ).reply()
            results["@id"] = (
                "%s/@querystring-search/%s"
                % (self.context.absolute_url(), self.params[0]),
            )
        else:
            results = self.getResults()
            results = getMultiAdapter((results, self.request), ISerializeToJson)(
                fullobjects=fullobjects
            )
        return results

    def setQuerybuilderParams(self):
        data = json_body(self.request)
        query = data.get("query", None)
        b_start = int(data.get("b_start", 0))
        b_size = int(data.get("b_size", 25))
        sort_on = data.get("sort_on", None)
        sort_order = data.get("sort_order", None)
        limit = int(data.get("limit", 1000))

        if query is None:
            raise Exception("No query supplied")

        if sort_order:
            sort_order = "descending" if sort_order == "descending" else "ascending"

        self.querybuilder_params = dict(
            query=query,
            brains=True,
            b_start=b_start,
            b_size=b_size,
            sort_on=sort_on,
            sort_order=sort_order,
            limit=limit,
        )

    def getResults(self):
        querybuilder = getMultiAdapter(
            (self.context, self.request), name="querybuilderresults"
        )

        # Exclude "self" content item from the results when ZCatalog supports NOT UUID
        # queries and it is called on a content object.
        if not IPloneSiteRoot.providedBy(self.context) and SUPPORT_NOT_UUID_QUERIES:
            self.querybuilder_params.update(
                dict(custom_query={"UID": {"not": self.context.UID()}})
            )

        return querybuilder(**self.querybuilder_params)


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


class QuerystringSearchGet(Service):
    """Returns the querystring search results given a p.a.querystring data."""

    def reply(self):
        # We need to copy the JSON query parameters from the querystring
        # into the request body, because that's where other code expects to find them
        self.request["BODY"] = parse.unquote(
            self.request.form.get("query", "{}")
        ).encode(self.request.charset)

        # unset the get parameters
        self.request.form = {}
        querystring_search = QuerystringSearch(self.context, self.request)
        return querystring_search()
