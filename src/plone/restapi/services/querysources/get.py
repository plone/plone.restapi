from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services.sources.get import get_field_by_name
from plone.restapi.services.sources.get import SourcesGet
from z3c.formwidget.query.interfaces import IQuerySource
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class QuerySourcesGet(SourcesGet):
    def reply(self):
        if len(self.params) != 1:
            return self._error(
                400, "Bad Request", "Must supply exactly one path parameter (fieldname)"
            )
        fieldname = self.params[0]

        field = get_field_by_name(fieldname, self.context)
        if field is None:
            return self._error(404, "Not Found", "No such field: %r" % fieldname)
        bound_field = field.bind(self.context)

        source = bound_field.source
        if not IQuerySource.providedBy(source):
            return self._error(
                404, "Not Found", "Field %r does not have an IQuerySource" % fieldname
            )

        if "query" not in self.request.form:
            return self._error(
                400,
                "Bad Request",
                "Enumerating querysources is not supported. Please search "
                "the source using the ?query= QS parameter",
            )

        query = self.request.form["query"]

        result = source.search(query)

        terms = []
        for term in result:
            terms.append(term)

        batch = HypermediaBatch(self.request, terms)

        serialized_terms = []
        for term in batch:
            serializer = getMultiAdapter(
                (term, self.request), interface=ISerializeToJson
            )
            serialized_terms.append(serializer())

        result = {
            "@id": batch.canonical_url,
            "items": serialized_terms,
            "items_total": batch.items_total,
        }
        links = batch.links
        if links:
            result["batching"] = links
        return result
