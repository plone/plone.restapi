# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from plone.restapi.pas.plugin import JWTAuthenticationPlugin


def install_pas_plugin(context):
    uf_parent = aq_inner(context)
    while True:
        uf = getToolByName(uf_parent, 'acl_users')
        if 'jwt_auth' not in uf:
            plugin = JWTAuthenticationPlugin('jwt_auth')
            uf._setObject(plugin.getId(), plugin)
            plugin = uf['jwt_auth']
            plugin.manage_activateInterfaces([
                'IAuthenticationPlugin',
                'IExtractionPlugin',
            ])
        if uf_parent is uf_parent.getPhysicalRoot():
            break
        uf_parent = aq_parent(uf_parent)


def import_various(context):
    """Miscellanous steps import handle
    """
    if context.readDataFile('plone.restapi_various.txt') is None:
        return

    site = context.getSite()
    install_pas_plugin(site)
