# -*- coding: utf-8 -*-
from AccessControl import allow_module
from AccessControl.Permissions import add_user_folders
from plone.restapi.pas import plugin
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from zope.i18nmessageid import MessageFactory

import pkg_resources


_ = MessageFactory("plone.restapi")
PROJECT_NAME = "plone.restapi"


allow_module("json")

try:
    pkg_resources.get_distribution("plone.app.testing")
    REGISTER_TEST_TYPES = True
except pkg_resources.DistributionNotFound:  # pragma: no cover
    REGISTER_TEST_TYPES = False

try:
    pkg_resources.get_distribution("plone.app.contenttypes")
    HAS_PLONE_APP_CONTENTTYPES = True
except pkg_resources.DistributionNotFound:  # pragma: no cover
    HAS_PLONE_APP_CONTENTTYPES = False

try:
    pkg_resources.get_distribution("Products.Archetypes")
except pkg_resources.DistributionNotFound:
    HAS_AT = False
else:
    HAS_AT = True


def initialize(context):
    registerMultiPlugin(plugin.JWTAuthenticationPlugin.meta_type)
    context.registerClass(
        plugin.JWTAuthenticationPlugin,
        permission=add_user_folders,
        constructors=(
            plugin.manage_addJWTAuthenticationPlugin,
            plugin.addJWTAuthenticationPlugin,
        ),
        visibility=None,
    )

    if HAS_AT and REGISTER_TEST_TYPES:
        from Products.Archetypes.ArchetypeTool import process_types, listTypes
        from Products.CMFCore import permissions
        from Products.CMFCore import utils
        from plone.restapi.tests.attypes import PROJECTNAME

        content_types, constructors, ftis = process_types(
            listTypes(PROJECTNAME), PROJECTNAME
        )

        utils.ContentInit(
            "%s Content" % PROJECTNAME,
            content_types=content_types,
            permission=permissions.AddPortalContent,
            extra_constructors=constructors,
            fti=ftis,
        ).initialize(context)
