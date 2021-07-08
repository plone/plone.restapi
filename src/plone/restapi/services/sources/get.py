from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IIterableSource
from zope.schema.interfaces import ISource


@implementer(IPublishTraverse)
class SourcesGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@sources as parameters
        self.params.append(name)
        return self

    def _error(self, status, type, message):
        self.request.response.setStatus(status)
        return {"error": {"type": type, "message": message}}

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
        if not ISource.providedBy(source):
            return self._error(
                404, "Not Found", "Field %r does not have a source" % fieldname
            )

        if not IIterableSource.providedBy(source):
            return self._error(
                400, "Bad Request", "Source for field %r is not iterable. " % fieldname
            )

        serializer = getMultiAdapter((source, self.request), interface=ISerializeToJson)
        return serializer(f"{self.context.absolute_url()}/@sources/{fieldname}")


def get_field_by_name(fieldname, context):
    schemata = iterSchemata(context)
    for schema in schemata:
        fields = getFieldsInOrder(schema)
        for fn, field in fields:
            if fn == fieldname:
                return field
