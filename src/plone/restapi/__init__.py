from . import patches  # noqa: ignore=F401
from AccessControl.Permissions import add_user_folders
from importlib import import_module
from importlib.metadata import distribution
from importlib.metadata import PackageNotFoundError
from plone.restapi.pas import plugin
from Products.PluggableAuthService.PluggableAuthService import registerMultiPlugin
from zope.i18nmessageid import MessageFactory


try:
    distribution("plone.app.multilingual")
    HAS_MULTILINGUAL = True
except PackageNotFoundError:
    HAS_MULTILINGUAL = False

_ = MessageFactory("plone.restapi")
PROJECT_NAME = "plone.restapi"


# BBB: Plone 5.2
HAS_PLONE_6 = getattr(
    import_module("Products.CMFPlone.factory"), "PLONE60MARKER", False
)


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
