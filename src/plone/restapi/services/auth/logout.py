# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin


class Logout(Service):
    """Handles logout by invalidating the JWT"""

    def reply(self):
        plugin = None
        acl_users = getToolByName(self, "acl_users")
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
            self.request.response.setStatus(501)
            return dict(
                error=dict(type="Logout failed", message="Token can't be invalidated")
            )

        creds = plugin.extractCredentials(self.request)
        if creds and "token" in creds and plugin.delete_token(creds["token"]):
            self.request.response.setStatus(200)
            return super(Logout, self).reply()

        self.request.response.setStatus(400)
        return dict(error=dict(type="Logout failed", message="Unknown token"))
