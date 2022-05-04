from plone.restapi import pas
from plone.restapi.pas.plugin import JWTAuthenticationPlugin
from Products.CMFPlone.interfaces import INonInstallable
from zope.component.hooks import getSite
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):  # pragma: no cover
        """Do not show on Plone's list of installable profiles."""
        return [
            "plone.restapi:blocks",
            "plone.restapi:performance",
            "plone.restapi:testing",
            "plone.restapi:testing-workflows",
            "plone.restapi:uninstall",
        ]

    def getNonInstallableProducts(self):  # pragma: no cover
        """Do not show on Plone's list of installable products.

        This method is only used in Plone 5.1+.
        """
        return ["plone.restapi.upgrades"]


def install_pas_plugin(context):
    """
    Install the JWT token PAS plugin in every PAS acl_users here and above.

    Usually this means it is installed into Plone and into the Zope root.
    """
    for uf, is_plone_site in pas.iter_ancestor_pas(context):

        # Add the API token plugin if not already installed at this level
        if "jwt_auth" not in uf:
            plugin = JWTAuthenticationPlugin("jwt_auth")
            uf._setObject(plugin.getId(), plugin)
            plugin = uf["jwt_auth"]
            plugin.manage_activateInterfaces(
                [
                    "IAuthenticationPlugin",
                    "IExtractionPlugin",
                    "ICredentialsUpdatePlugin",
                    "ICredentialsResetPlugin",
                ],
            )


def post_install_default(context):
    """Post install of default profile"""
    site = getSite()
    install_pas_plugin(site)
