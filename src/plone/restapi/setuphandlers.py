# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.restapi.pas.plugin import JWTAuthenticationPlugin
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable
from Products.PluggableAuthService.interfaces.authservice import (
    IPluggableAuthService,
)  # noqa: E501
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):  # pragma: no cover
        """Do not show on Plone's list of installable profiles."""
        return [
            u"plone.restapi:performance",
            u"plone.restapi:testing",
            u"plone.restapi:blocks",
            u"plone.restapi:uninstall",
        ]

    def getNonInstallableProducts(self):  # pragma: no cover
        """Do not show on Plone's list of installable products.

        This method is only used in Plone 5.1+.
        """
        return [u"plone.restapi.upgrades"]


def install_pas_plugin(context):
    uf_parent = aq_inner(context)
    while True:
        uf = getToolByName(uf_parent, "acl_users")
        if IPluggableAuthService.providedBy(uf) and "jwt_auth" not in uf:
            plugin = JWTAuthenticationPlugin("jwt_auth")
            uf._setObject(plugin.getId(), plugin)
            plugin = uf["jwt_auth"]
            plugin.manage_activateInterfaces(
                ["IAuthenticationPlugin", "IExtractionPlugin"]
            )
        if uf_parent is uf_parent.getPhysicalRoot():
            break
        uf_parent = aq_parent(uf_parent)


def import_various(context):
    """Miscellanous steps import handle"""
    if context.readDataFile("plone.restapi_various.txt") is None:
        return

    site = context.getSite()
    install_pas_plugin(site)
