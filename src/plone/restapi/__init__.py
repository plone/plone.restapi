# -*- coding: utf-8 -*-
from AccessControl import allow_module
from AccessControl.Permissions import add_user_folders
from Products.PluggableAuthService.PluggableAuthService import (
    registerMultiPlugin)
from plone.restapi.pas import plugin

import pkg_resources

allow_module('json')

try:
    pkg_resources.get_distribution('plone.app.testing')
except pkg_resources.DistributionNotFound:
    REGISTER_TEST_TYPES = False
else:
    REGISTER_TEST_TYPES = True


try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    HAS_PLONE_APP_CONTENTTYPES = False
else:
    HAS_PLONE_APP_CONTENTTYPES = True


def initialize(context):
    registerMultiPlugin(plugin.JWTAuthenticationPlugin.meta_type)
    context.registerClass(
        plugin.JWTAuthenticationPlugin,
        permission=add_user_folders,
        constructors=(plugin.manage_addJWTAuthenticationPlugin,
                      plugin.addJWTAuthenticationPlugin),
        visibility=None,
    )

    if REGISTER_TEST_TYPES:
        from Products.Archetypes.ArchetypeTool import process_types, listTypes
        from Products.CMFCore import permissions
        from Products.CMFCore import utils
        from plone.restapi.tests.attypes import PROJECTNAME

        content_types, constructors, ftis = process_types(
            listTypes(PROJECTNAME), PROJECTNAME)

        utils.ContentInit(
            '%s Content' % PROJECTNAME,
            content_types=content_types,
            permission=permissions.AddPortalContent,
            extra_constructors=constructors,
            fti=ftis,
        ).initialize(context)
