# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import getMultiAdapter


class QuerystringSearchPost(Service):
    """Returns the querystring search results given a p.a.querystring data.
    """

    def reply(self):
        data = json_body(self.request)
        query = data.get("query", None)
        b_start = int(data.get("b_start", 0))
        b_size = int(data.get("b_size", 25))
        sort_on = data.get("sort_on", None)
        sort_order = data.get("sort_order", None)
        limit = int(data.get("limit", 1000))
        fullobjects = data.get("fullobjects", False)

        if query is None:
            raise Exception("No query supplied")

        if sort_order:
            sort_order = "descending" if sort_order else "ascending"

        querybuilder = getMultiAdapter(
            (self.context, self.request), name="querybuilderresults"
        )
        results = querybuilder(
            query=query,
            brains=True,
            b_start=b_start,
            b_size=b_size,
            sort_on=sort_on,
            sort_order=sort_order,
            limit=limit,
        )

        results = getMultiAdapter((results, self.request), ISerializeToJson)(
            fullobjects=fullobjects
        )
        return results
