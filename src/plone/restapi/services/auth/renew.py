# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import (
    IAuthenticationPlugin)
from plone.restapi.services import Service


class Renew(Service):
    """Renew authentication token
    """
    def reply(self):
        plugin = None
        acl_users = getToolByName(self, "acl_users")
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

        mtool = getToolByName(self.context, 'portal_membership')
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
