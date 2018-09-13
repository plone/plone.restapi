# -*- coding: utf-8 -*-
from plone.restapi.pas.plugin import JWTAuthenticationPlugin
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):  # pragma: no cover
        """Do not show on Plone's list of installable profiles."""
        return [
            u'plone.restapi:uninstall',
        ]

    def getNonInstallableProducts(self):  # pragma: no cover
        """Do not show on Plone's list of installable products.

        This method is only used in Plone 5.1+.
        """
        return [
            u'plone.restapi.upgrades',
        ]


def install_pas_plugin(context):
    uf = getToolByName(context, 'acl_users', None)
    if uf is None:
        return

    if 'jwt_auth' not in uf:
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
