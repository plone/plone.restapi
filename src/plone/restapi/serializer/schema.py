from AccessControl import getSecurityManager
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISchemaSerializer
from plone.restapi.serializer.converters import json_compatible
from plone.supermodel.utils import mergedTaggedValueDict
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.schema import getFields
from zope.security.interfaces import IPermission


@adapter(IInterface, Interface, Interface)
@implementer(ISchemaSerializer)
class SerializeSchemaToJson:
    """Serialize fields from a single schema, honoring read permissions."""

    def __init__(self, schema, context, request):
        self.context = context
        self.request = request
        self.schema = schema

    def __call__(self):
        result = {}

        read_permissions = mergedTaggedValueDict(self.schema, READ_PERMISSIONS_KEY)
        for name, field in getFields(self.schema).items():
            if not _check_permission(read_permissions.get(name), self):
                continue
            serializer = getMultiAdapter(
                (field, self.context, self.request), IFieldSerializer
            )
            value = serializer()
            result[json_compatible(name)] = value

        return result


def _check_permission(permission_name, instance, obj=None) -> bool:
    if permission_name is None:
        return True
    if obj is None:
        obj = instance.context

    permission_cache = getattr(instance, "_permission_cache", {})
    if not permission_cache:
        instance._permission_cache = permission_cache

    if permission_name not in permission_cache:
        permission = queryUtility(IPermission, name=permission_name)
        if permission is None:
            permission_cache[permission_name] = True
        else:
            sm = getSecurityManager()
            permission_cache[permission_name] = bool(
                sm.checkPermission(permission.title, obj)
            )
    return permission_cache[permission_name]
