# -*- coding: utf-8 -*-
from plone.restapi.pas.plugin import JWTAuthenticationPlugin
import plone.api.portal


def install_pas_plugin(context):
    uf = plone.api.portal.get_tool('acl_users')
    if 'jwt_auth' in uf:
        return
    plugin = JWTAuthenticationPlugin('jwt_auth')
    uf._setObject(plugin.getId(), plugin)
    plugin = uf['jwt_auth']
    plugin.manage_activateInterfaces([
        'IAuthenticationPlugin',
        'IExtractionPlugin',
    ])


def import_various(context):
    """Miscellanous steps import handle
    """
    if context.readDataFile('plone.restapi_various.txt') is None:
        return

    site = context.getSite()
    install_pas_plugin(site)
