# -*- coding: utf-8 -*-

from AccessControl import allow_module
from AccessControl.Permissions import add_user_folders
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin  # NOQA: E501
from plone.restapi.pas import plugin

import pkg_resources

allow_module('json')

try:
    pkg_resources.get_distribution('plone.app.testing')
    REGISTER_TEST_TYPES = True
except pkg_resources.DistributionNotFound:
    REGISTER_TEST_TYPES = False

try:
    pkg_resources.get_distribution('plone.app.contenttypes')
    HAS_PLONE_APP_CONTENTTYPES = True

    event_version = pkg_resources.get_distribution('plone.app.event').version
    if pkg_resources.parse_version(event_version) > \
       pkg_resources.parse_version('1.99'):
        HAS_PLONE_APP_EVENT_20 = True
    else:
        HAS_PLONE_APP_EVENT_20 = False

except pkg_resources.DistributionNotFound:
    HAS_PLONE_APP_CONTENTTYPES = False
    HAS_PLONE_APP_EVENT_20 = False


def initialize(context):
    registerMultiPlugin(plugin.JWTAuthenticationPlugin.meta_type)
    context.registerClass(
        plugin.JWTAuthenticationPlugin,
        permission=add_user_folders,
        constructors=(
            plugin.manage_addJWTAuthenticationPlugin,
            plugin.addJWTAuthenticationPlugin
        ),
        visibility=None,
    )

    if REGISTER_TEST_TYPES:
        from Products.Archetypes.ArchetypeTool import process_types, listTypes
        from Products.CMFCore import permissions
        from Products.CMFCore import utils
        from plone.restapi.tests.attypes import PROJECTNAME

        content_types, constructors, ftis = process_types(
            listTypes(PROJECTNAME),
            PROJECTNAME
        )

        utils.ContentInit(
            '%s Content' % PROJECTNAME,
            content_types=content_types,
            permission=permissions.AddPortalContent,
            extra_constructors=constructors,
            fti=ftis,
        ).initialize(context)
