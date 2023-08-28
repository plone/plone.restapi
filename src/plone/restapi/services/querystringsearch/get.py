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


zcatalog_version = get_distribution("Products.ZCatalog").version
if parse_version(zcatalog_version) >= parse_version("5.1"):
    SUPPORT_NOT_UUID_QUERIES = True
else:
    SUPPORT_NOT_UUID_QUERIES = False


class QuerystringSearch:
    """Returns the querystring search results given a p.a.querystring data."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
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
        fullobjects = bool(data.get("fullobjects", False))

        if not query:
            raise BadRequest("No query supplied")

        if sort_order:
            sort_order = "descending" if sort_order == "descending" else "ascending"

        querybuilder = getMultiAdapter(
            (self.context, self.request), name="querybuilderresults"
        )

        querybuilder_parameters = dict(
            query=query,
            brains=True,
            b_start=b_start,
            b_size=b_size,
            sort_on=sort_on,
            sort_order=sort_order,
            limit=limit,
        )

        # Exclude "self" content item from the results when ZCatalog supports NOT UUID
        # queries and it is called on a content object.
        if not IPloneSiteRoot.providedBy(self.context) and SUPPORT_NOT_UUID_QUERIES:
            querybuilder_parameters.update(
                dict(custom_query={"UID": {"not": self.context.UID()}})
            )

        try:
            results = querybuilder(**querybuilder_parameters)
        except KeyError:
            # This can happen if the query has an invalid operation,
            # but plone.app.querystring doesn't raise an exception
            # with specific info.
            raise BadRequest("Invalid query.")

        results = getMultiAdapter((results, self.request), ISerializeToJson)(
            fullobjects=fullobjects
        )
        return results


class QuerystringSearchPost(Service):
    """Returns the querystring search results given a p.a.querystring data."""

    def reply(self):
        querystring_search = QuerystringSearch(self.context, self.request)
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
