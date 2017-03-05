# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin  # noqa
from zope.interface import alsoProvides

import plone.protect.interfaces
import plone.api.portal


class Renew(Service):
    """Renew authentication token
    """
    def reply(self):
        plugin = None
        acl_users = plone.api.portal.get_tool("acl_users")
        plugins = acl_users._getOb('plugins')
        authenticators = plugins.listPlugins(IAuthenticationPlugin)
        for id_, authenticator in authenticators:
            if authenticator.meta_type == "JWT Authentication Plugin":
                plugin = authenticator
                break

        if plugin is None:
            self.request.response.setStatus(501)
            return dict(error=dict(
                type='Renew failed',
                message='JWT authentication plugin not installed.'))

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        mtool = plone.api.portal.get_tool('portal_membership')
        user = mtool.getAuthenticatedMember()
        payload = {}
        payload['fullname'] = user.getProperty('fullname')
        new_token = plugin.create_token(user.getId(), data=payload)
        if plugin.store_tokens and self.request._auth:
            old_token = self.request._auth[7:]
            plugin.delete_token(old_token)
        return {
            'token': new_token
        }
