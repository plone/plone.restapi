from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISchemaSerializer
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.permissions import check_permission
from plone.supermodel.utils import mergedTaggedValueDict
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from plone.dexterity.content import DexterityContent
from zope.interface.interfaces import IInterface
from plone.dexterity.interfaces import IContentType
from ZPublisher.HTTPRequest import HTTPRequest


class BaseSerializer:
    def __init__(self, schema, context: DexterityContent, request: HTTPRequest):
        self.schema = schema
        self.context = context
        self.request = request
        self.permission_cache = {}

    def __call__(self):
        result = {}
        schema = self.schema
        read_permissions = mergedTaggedValueDict(schema, READ_PERMISSIONS_KEY)
        for name, field in getFields(schema).items():
            if not check_permission(
                read_permissions.get(name), self.context, self.permission_cache
            ):
                continue

            # serialize the field
            serializer = queryMultiAdapter(
                (field, self.context, self.request), IFieldSerializer
            )
            value = serializer()
            result[json_compatible(name)] = value
        return result


@implementer(ISchemaSerializer)
@adapter(IInterface, IDexterityContent, Interface)
class SerializeSchemaToJson(BaseSerializer):
    """Serialize ISchema to JSON."""


@implementer(ISchemaSerializer)
@adapter(IContentType, IDexterityContent, Interface)
class DXSchemaSerializeToJson(BaseSerializer):
    """Serialize IDexteritySchema to JSON."""
