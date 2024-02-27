from . import patches  # noqa: ignore=F401
from AccessControl import allow_module
from AccessControl.Permissions import add_user_folders
from plone.restapi.pas import plugin
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from zope.i18nmessageid import MessageFactory

import pkg_resources

try:
    pkg_resources.get_distribution("plone.app.multilingual")
    HAS_MULTILINGUAL = True
except pkg_resources.DistributionNotFound:
    HAS_MULTILINGUAL = False

_ = MessageFactory("plone.restapi")
PROJECT_NAME = "plone.restapi"


allow_module("json")


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
