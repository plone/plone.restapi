from AccessControl.requestmethod import postonly
from AccessControl.SecurityInfo import ClassSecurityInfo
from BTrees.OIBTree import OIBTree
from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from datetime import datetime
from datetime import timedelta
from plone.keyring.interfaces import IKeyManager
from plone.keyring.keyring import GenerateSecret
from plone.restapi import exceptions
from plone.restapi import deserializer
from Products.CMFCore.permissions import ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.interfaces.plugins import ICredentialsUpdatePlugin
from Products.PluggableAuthService.interfaces.plugins import ICredentialsResetPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from zope import component
from zope.component import getUtility
from zope.interface import implementer

import jwt
import logging
import time

logger = logging.getLogger(__name__)

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

if version("pyjwt")[0] == "1":
    OLD_JWT = True
else:
    OLD_JWT = False

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


@implementer(
    IAuthenticationPlugin,
    IChallengePlugin,
    IExtractionPlugin,
    ICredentialsUpdatePlugin,
    ICredentialsResetPlugin,
)
class JWTAuthenticationPlugin(BasePlugin):
    """Plone PAS plugin for authentication with JSON web tokens (JWT)."""

    meta_type = "JWT Authentication Plugin"
    security = ClassSecurityInfo()

    token_timeout = 60 * 60 * 12  # 12 hours
    use_keyring = True
    store_tokens = False
    _secret = None
    _tokens = None
    cookie_name = "auth_token"

    # ZMI tab for configuration page
    manage_options = (
        {"label": "Configuration", "action": "manage_config"},
    ) + BasePlugin.manage_options
    security.declareProtected(ManagePortal, "manage_config")
    manage_config = PageTemplateFile("config", globals(), __name__="manage_config")

    def __init__(self, id_, title=None, cookie_name=None):
        self._setId(id_)
        self.title = title
        if cookie_name:
            self.cookie_name = cookie_name

    # Initiate a challenge to the user to provide credentials.
    @security.private
    def challenge(self, request, response, **kw):

        realm = response.realm
        if realm:
            response.setHeader("WWW-Authenticate", 'Bearer realm="%s"' % realm)
        m = "You are not authorized to access this resource."

        response.setBody(m, is_error=1)
        response.setStatus(401)
        return True

    # IExtractionPlugin implementation
    # Extracts a JSON web token from the request.
    @security.private
    def extractCredentials(self, request):
        """
        Extract credentials either from a JSON POST request or an established JWT token.
        """
        # Prefer any credentials in a JSON POST request under the assumption that any
        # such requested sent when a JWT token is already in the `Authorization` header
        # is intended to change or update the logged in user.
        try:
            creds = deserializer.json_body(request)
        except exceptions.DeserializationError:
            pass
        else:
            if "login" in creds and "password" in creds:
                return creds

        creds = {}

        # Prefer the Authorization Bearer header if present
        auth = request._auth
        if auth is None:
            return
        if auth[:7].lower() == "bearer ":
            creds["token"] = auth.split()[-1]
            return creds

        # Finally, use the cookie if present
        cookie = request.get(self.cookie_name, "")
        if cookie:
            creds["token"] = cookie
            return creds

    # IAuthenticationPlugin implementation
    @security.private
    def authenticateCredentials(self, credentials):
        # Ignore credentials that are not from our extractor
        extractor = credentials.get("extractor")
        if extractor != self.getId():
            return

        payload = self._decode_token(credentials["token"])
        if not payload:
            return

        if "sub" not in payload:
            return

        userid = payload["sub"]

        if self.store_tokens:
            if userid not in self._tokens:
                return
            if credentials["token"] not in self._tokens[userid]:
                return

        return (userid, userid)

    @security.private
    def updateCredentials(self, request, response, login, new_password):
        """
        Generate a new token for use both in the Bearer header and the cookie.
        """
        # Unfortunately PAS itself is confused as to whether this plugin method should
        # get the immutable user ID or the mutable, user-facing user login/name.  Real
        # usage in the Plone code base also uses both.  Do our best to guess which.
        user_id = login
        data = dict(fullname="")
        user = self._getPAS().getUserById(login)
        if user is None:
            user = self._getPAS().getUser(login)
        if user is not None:
            user_id = user.getId()
            data["fullname"] = user.getProperty("fullname")
        payload, token = self.create_payload_token(user_id, data=data)
        # Make available on the request for further use such as returning it in the JSON
        # body of the response if the current request is for the REST API login view.
        request[self.cookie_name] = token
        # Make the token available to the client browser for use in UI code such as when
        # the login happened through Plone Classic so that the the Volro React
        # components can retrieve the token that way and use the Authorization Bearer
        # header from then on.
        cookie_kwargs = {}
        if "exp" in payload:
            # Match the token expiration date/time.
            cookie_kwargs["expires"] = DateTime(payload["exp"]).toZone("GMT").rfc822()
        response.setCookie(
            self.cookie_name,
            token,
            path="/",
            **cookie_kwargs,
        )

    @security.private
    def resetCredentials(self, request, response):
        """
        Expire the token and remove the cookie.
        """
        if self.cookie_name in request:
            if self.store_tokens:
                self.delete_token(request[self.cookie_name])
            response.expireCookie(self.cookie_name, path="/")

    @security.protected(ManagePortal)
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
            manager = component.queryUtility(IKeyManager)
            if manager is None:
                logger.error(
                    "JWT token plugin configured to use IKeyManager "
                    "but no utility is registered: %r\n"
                    "Have you upgraded the `plone.restapi:default` profile?",
                    "/".join(self.getPhysicalPath()),
                )
                return
            for secret in manager["_system"]:
                if secret is None:
                    continue
                payload = self._jwt_decode(token, secret + self._path(), verify=verify)
                if payload is not None:
                    return payload
        else:
            return self._jwt_decode(token, self._secret + self._path(), verify=verify)

    def _jwt_decode(self, token, secret, verify=True):
        if isinstance(token, str):
            token = token.encode("utf-8")
        try:
            if OLD_JWT:
                return jwt.decode(token, secret, verify=verify, algorithms=["HS256"])
            return jwt.decode(
                token,
                secret,
                options={"verify_signature": verify},
                algorithms=["HS256"],
            )
        except jwt.InvalidTokenError:
            pass

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
        if not payload or "sub" not in payload:
            return False
        userid = payload["sub"]
        if userid in self._tokens and token in self._tokens[userid]:
            del self._tokens[userid][token]
            return True

    def create_payload_token(self, userid, timeout=None, data=None):
        """
        Create and return both a JWT payload and the signed token.
        """
        payload = {}
        payload["sub"] = userid
        if timeout is None:
            timeout = self.token_timeout
        if timeout:
            payload["exp"] = datetime.utcnow() + timedelta(seconds=timeout)
        if data is not None:
            payload.update(data)
        token = jwt.encode(payload, self._signing_secret(), algorithm="HS256")
        if OLD_JWT:
            token = token.decode("utf-8")
        if self.store_tokens:
            if self._tokens is None:
                self._tokens = OOBTree()
            if userid not in self._tokens:
                self._tokens[userid] = OIBTree()
            self._tokens[userid][token] = int(time.time())
        return payload, token

    def create_token(self, userid, timeout=None, data=None):
        """
        Create a JWT payload and the signed token, return the token.
        """
        _, token = self.create_payload_token(
            userid,
            timeout=timeout,
            data=data,
        )
        return token
