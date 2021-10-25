from AccessControl import allow_module
from AccessControl.Permissions import add_user_folders
from plone.restapi.pas import plugin
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from zope.i18nmessageid import MessageFactory


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
