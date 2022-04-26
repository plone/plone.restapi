"""
GenericSetup profile upgrades from version 0006 to 0007.
"""

from plone.restapi import pas
from plone.restapi.pas import plugin
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces import plugins as plugins_ifaces

import logging

logger = logging.getLogger(__name__)


def enable_new_pas_plugin_interfaces(context):
    """
    Enable new PAS plugin interfaces.

    After correcting/completing the PAS plugin interfaces, those interfaces need to be
    enabled for existing functionality to continue working.
    """
    portal = getToolByName(context, "portal_url").getPortalObject()
    for uf, is_plone_site in pas.iter_ancestor_pas(portal):
        for jwt_plugin in uf.objectValues(plugin.JWTAuthenticationPlugin.meta_type):
            if not is_plone_site and jwt_plugin.use_keyring:
                logger.info(
                    "Disabling keyring for plugin outside of Plone: %s",
                    "/".join(jwt_plugin.getPhysicalPath()),
                )
                jwt_plugin.use_keyring = False
            for new_iface in (
                plugins_ifaces.ICredentialsUpdatePlugin,
                plugins_ifaces.ICredentialsResetPlugin,
            ):
                active_plugin_ids = [
                    active_plugin_id
                    for active_plugin_id, _ in uf.plugins.listPlugins(new_iface)
                ]
                if jwt_plugin.id not in active_plugin_ids:
                    logger.info(
                        "Activating PAS interface %s: %s",
                        new_iface.__name__,
                        "/".join(jwt_plugin.getPhysicalPath()),
                    )
                    uf.plugins.activatePlugin(new_iface, jwt_plugin.id)
