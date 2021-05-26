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
