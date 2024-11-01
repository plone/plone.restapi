from plone.dexterity.content import DexterityContent
from zope.security.interfaces import IPermission
from AccessControl import getSecurityManager
from zope.component import queryUtility

# # Required to use the REST API at all, in addition to service specific
# permissions. Granted to Anonymous (i.e. everyone) by default via rolemap.xml

UseRESTAPI = "plone.restapi: Use REST API"

PloneManageUsers = "Plone Site Setup: Users and Groups"


def check_permission(
    permission_name: str, context: DexterityContent, permission_cache: dict = None
):
    if permission_name is None:
        return True
    elif permission_cache is None:
        permission_cache = {}

    if permission_name not in permission_cache:
        permission = queryUtility(IPermission, name=permission_name)
        if permission is None:
            permission_cache[permission_name] = True
        else:
            sm = getSecurityManager()
            permission_cache[permission_name] = bool(
                sm.checkPermission(permission.title, context)
            )
    return permission_cache[permission_name]
