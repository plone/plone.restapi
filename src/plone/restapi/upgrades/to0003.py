from plone.restapi.setuphandlers import install_pas_plugin
from Products.CMFCore.utils import getToolByName


def install_pas_plugin_in_zope_root(setup_context):
    """Install PAS plugin in Zope root"""
    portal = getToolByName(setup_context, "portal_url").getPortalObject()
    install_pas_plugin(portal)
