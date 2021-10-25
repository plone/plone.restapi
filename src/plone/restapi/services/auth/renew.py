from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import (
    IAuthenticationPlugin,
)  # noqa
from zope.interface import alsoProvides

import plone.protect.interfaces


class Renew(Service):
    """Renew authentication token"""

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
                    type="Renew failed",
                    message="JWT authentication plugin not installed.",
                )
            )

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        mtool = getToolByName(self.context, "portal_membership")
        if bool(mtool.isAnonymousUser()):
            # Don't generate authentication tokens for anonymous users.
            self.request.response.setStatus(401)
            return dict(
                error=dict(
                    type="Invalid or expired authentication token",
                    message="The authentication token is invalid or expired.",
                )
            )
        user = mtool.getAuthenticatedMember()
        payload = {}
        payload["fullname"] = user.getProperty("fullname")
        new_token = plugin.create_token(user.getId(), data=payload)
        if plugin.store_tokens and self.request._auth:
            old_token = self.request._auth[7:]
            plugin.delete_token(old_token)
        return {"token": new_token}
