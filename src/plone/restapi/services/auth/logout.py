from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin


class Logout(Service):
    """Handles logout by invalidating the JWT"""

    def reply(self):
        plugin = None
        acl_users = getToolByName(self, "acl_users")
        mt = getToolByName(self.context, "portal_membership")
        plugins = acl_users._getOb("plugins")
        authenticators = plugins.listPlugins(IAuthenticationPlugin)
        for id_, authenticator in authenticators:
            if authenticator.meta_type == "JWT Authentication Plugin":
                plugin = authenticator
                break

        if plugin is None:
            self.request.response.setStatus(501)
            return dict(
                error=dict(
                    type="Logout failed",
                    message="JWT authentication plugin not installed.",
                )
            )

        if not plugin.store_tokens:
            # Just logout properly from Plone
            mt.logoutUser()
            self.request.response.setStatus(200)
            return super().reply()

        creds = plugin.extractCredentials(self.request)
        if (
            plugin.store_tokens
            and creds
            and "token" in creds
            and plugin.delete_token(creds["token"])
        ):
            # Logout also properly from Plone
            mt.logoutUser()
            self.request.response.setStatus(200)
            return super().reply()

        self.request.response.setStatus(400)
        return dict(error=dict(type="Logout failed", message="Unknown token"))
