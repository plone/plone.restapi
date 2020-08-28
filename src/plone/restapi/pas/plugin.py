# -*- coding: utf-8 -*-
from AccessControl.requestmethod import postonly
from AccessControl.SecurityInfo import ClassSecurityInfo
from BTrees.OIBTree import OIBTree
from BTrees.OOBTree import OOBTree
from datetime import datetime
from datetime import timedelta
from plone.keyring.interfaces import IKeyManager
from plone.keyring.keyring import GenerateSecret
from Products.CMFCore.permissions import ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from zope.component import getUtility
from zope.interface import implementer

import jwt
import six
import time


manage_addJWTAuthenticationPlugin = PageTemplateFile(
    "add_plugin", globals(), __name__="manage_addJWTAuthenticationPlugin"
)


def addJWTAuthenticationPlugin(self, id_, title=None, REQUEST=None):
    """Add a JWT authentication plugin"""
    plugin = JWTAuthenticationPlugin(id_, title)
    self._setObject(plugin.getId(), plugin)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect(
            "%s/manage_workspace"
            "?manage_tabs_message=JWT+authentication+plugin+added."
            % self.absolute_url()
        )


@implementer(IAuthenticationPlugin, IChallengePlugin, IExtractionPlugin)
class JWTAuthenticationPlugin(BasePlugin):
    """Plone PAS plugin for authentication with JSON web tokens (JWT)."""

    meta_type = "JWT Authentication Plugin"
    security = ClassSecurityInfo()

    token_timeout = 60 * 60 * 12  # 12 hours
    use_keyring = True
    store_tokens = False
    _secret = None
    _tokens = None

    # ZMI tab for configuration page
    manage_options = (
        {"label": "Configuration", "action": "manage_config"},
    ) + BasePlugin.manage_options
    security.declareProtected(ManagePortal, "manage_config")
    manage_config = PageTemplateFile("config", globals(), __name__="manage_config")

    def __init__(self, id_, title=None):
        self._setId(id_)
        self.title = title

    security.declarePrivate("challenge")

    # Initiate a challenge to the user to provide credentials.
    def challenge(self, request, response, **kw):

        realm = response.realm
        if realm:
            response.setHeader("WWW-Authenticate", 'Bearer realm="%s"' % realm)
        m = "You are not authorized to access this resource."

        response.setBody(m, is_error=1)
        response.setStatus(401)
        return True

    security.declarePrivate("extractCredentials")

    # IExtractionPlugin implementation
    # Extracts a JSON web token from the request.
    def extractCredentials(self, request):
        creds = {}
        auth = request._auth
        if auth is None:
            return None
        if auth[:7].lower() == "bearer ":
            creds["token"] = auth.split()[-1]
        else:
            return None

        return creds

    security.declarePrivate("authenticateCredentials")

    # IAuthenticationPlugin implementation
    def authenticateCredentials(self, credentials):
        # Ignore credentials that are not from our extractor
        extractor = credentials.get("extractor")
        if extractor != self.getId():
            return None

        payload = self._decode_token(credentials["token"])
        if not payload:
            return None

        if "sub" not in payload:
            return None

        userid = payload["sub"]
        if six.PY2:
            userid = userid.encode("utf8")

        if self.store_tokens:
            if userid not in self._tokens:
                return None
            if credentials["token"] not in self._tokens[userid]:
                return None

        return (userid, userid)

    security.declareProtected(ManagePortal, "manage_updateConfig")

    @postonly
    def manage_updateConfig(self, REQUEST):
        """Update configuration of JWT Authentication Plugin."""
        response = REQUEST.response

        self.token_timeout = int(REQUEST.form.get("token_timeout", self.token_timeout))
        self.use_keyring = bool(REQUEST.form.get("use_keyring", False))
        self.store_tokens = bool(REQUEST.form.get("store_tokens", False))
        if self.store_tokens and self._tokens is None:
            self._tokens = OOBTree()

        response.redirect(
            "%s/manage_config?manage_tabs_message=%s"
            % (self.absolute_url(), "Configuration+updated.")
        )

    def _decode_token(self, token, verify=True):
        if self.use_keyring:
            manager = getUtility(IKeyManager)
            for secret in manager[u"_system"]:
                if secret is None:
                    continue
                payload = self._jwt_decode(token, secret + self._path(), verify=verify)
                if payload is not None:
                    return payload
        else:
            return self._jwt_decode(token, self._secret + self._path(), verify=verify)

    def _jwt_decode(self, token, secret, verify=True):
        if isinstance(token, six.text_type):
            token = token.encode("utf-8")
        try:
            return jwt.decode(token, secret, verify=verify, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return None

    def _signing_secret(self):
        if self.use_keyring:
            manager = getUtility(IKeyManager)
            return manager.secret() + self._path()
        if not self._secret:
            self._secret = GenerateSecret()
        return self._secret + self._path()

    def _path(self):
        return "/".join(self.getPhysicalPath())

    def delete_token(self, token):
        payload = self._decode_token(token, verify=False)
        if "sub" not in payload:
            return False
        userid = payload["sub"]
        if userid in self._tokens and token in self._tokens[userid]:
            del self._tokens[userid][token]
            return True

    def create_token(self, userid, timeout=None, data=None):
        payload = {}
        payload["sub"] = userid
        if timeout is None:
            timeout = self.token_timeout
        if timeout:
            payload["exp"] = datetime.utcnow() + timedelta(seconds=timeout)
        if data is not None:
            payload.update(data)
        token = jwt.encode(payload, self._signing_secret(), algorithm="HS256")
        if not six.PY2:
            token = token.decode("utf-8")
        if self.store_tokens:
            if self._tokens is None:
                self._tokens = OOBTree()
            if userid not in self._tokens:
                self._tokens[userid] = OIBTree()
            self._tokens[userid][token] = int(time.time())
        return token
