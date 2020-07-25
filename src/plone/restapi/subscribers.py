# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IPloneRestapiLayer
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from zope.component import adapter
from zope.globalrequest import getRequest


@adapter(IUserLoggedInEvent)
def onUserLogsIn(event):
    req = getRequest()
    if IPloneRestapiLayer.providedBy(req):
        user = event.principal
        uf = user.aq_parent
        plugins = uf._getOb("plugins")
        authenticators = plugins.listPlugins(IAuthenticationPlugin)
        plugin = None
        for id_, authenticator in authenticators:
            if authenticator.meta_type == "JWT Authentication Plugin":
                plugin = authenticator
                break
        if plugin:
            payload = {}
            payload["fullname"] = user.getProperty("fullname")
            token = plugin.create_token(user.getId(), data=payload)
            # TODO: take care of path and domain options ?
            req.response.setCookie('auth_token', token, path='/')

