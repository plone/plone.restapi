"""
A JWT token authentication plugin for PluggableAuthService.
"""

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import interfaces as plone_ifaces
from Products import PluggableAuthService  # noqa, Ensure PAS patch in place
from Products.PluggableAuthService.interfaces import authservice as authservice_ifaces

import Acquisition


def iter_ancestor_pas(context):
    """
    Walk up the ZODB OFS returning Pluggableauthservice `./acl_users/` for each level.
    """
    uf_parent = Acquisition.aq_inner(context)
    while True:
        is_plone_site = plone_ifaces.IPloneSiteRoot.providedBy(uf_parent)
        uf = getToolByName(uf_parent, "acl_users", default=None)

        # Skip ancestor contexts to which we don't/can't apply
        if uf is None or not authservice_ifaces.IPluggableAuthService.providedBy(uf):
            uf_parent = Acquisition.aq_parent(uf_parent)
            continue

        yield uf, is_plone_site

        # Go up one more level
        if uf_parent is uf_parent.getPhysicalRoot():
            break
        uf_parent = Acquisition.aq_parent(uf_parent)
