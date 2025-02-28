from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.model import ErrorOutputDTO
from pydantic import ValidationError
from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.interfaces.plugins import (
    IAuthenticationPlugin,
)
from zope import component
from zope.interface import alsoProvides

from .model import LoginInputDTO, TokenOutputDTO

import plone.protect.interfaces


class Login(Service):
    """Handles login and returns a JSON web token (JWT)."""

    @classmethod
    def __restapi_doc__(cls):
        return {
            "post": {
                "summary": "Login endpoint",
                "description": "A JWT token can be acquired by posting a user's credentials to the @login endpoint",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": LoginInputDTO.schema(),
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "User succesfully authenticated",
                        "content": {
                            "application/json": {
                                "schema": TokenOutputDTO.schema()
                            }
                        },
                    },
                    "400": {
                        "description": "User input error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "User unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        },
                    },
                    "501": {
                        "description": "Server error",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ErrorResponse"
                                }
                            }
                        },
                    },
                },
            }
        }

    def reply(self):
        try:
            data = LoginInputDTO(**json_body(self.request))
        except ValidationError as e:
            self.request.response.setStatus(400)
            return ErrorOutputDTO(
                error={
                    "type": "Missing credentials",
                    "message": "Login and password must be provided in body.",
                }
            ).dict()

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(
                self.request, plone.protect.interfaces.IDisableCSRFProtection
            )

        userid = data.login
        password = data.password
        uf = self._find_userfolder(userid)

        # Also put the password in __ac_password on the request.
        # The post-login code in PlonePAS expects to find it there
        # when it calls the PAS updateCredentials plugin.
        self.request.form["__ac_password"] = password

        if uf is not None:
            plugins = uf._getOb("plugins")
            authenticators = plugins.listPlugins(IAuthenticationPlugin)
            plugin = None
            for id_, authenticator in authenticators:
                if authenticator.meta_type == "JWT Authentication Plugin":
                    plugin = authenticator
                    break

            if plugin is None:
                self.request.response.setStatus(501)
                return ErrorOutputDTO(
                    error=dict(
                        type="Login failed",
                        message="JWT authentication plugin not installed.",
                    )
                ).dict()

            user = uf.authenticate(userid, password, self.request)
        else:
            user = None

        if not user:
            self.request.response.setStatus(401)
            return ErrorOutputDTO(
                error=dict(
                    type="Invalid credentials",
                    message="Wrong login and/or password.",
                )
            ).dict()

        # Perform the same post-login actions as would happen when logging in through
        # the Plone classic HTML login form.  There is a trade-off here, we either
        # violate DRY and duplicate the code from the classic HTML Plone view that will
        # then become out of date all the time, or we re-use the code from the core
        # Plone view and introduce a dependency we may have to update over time.  After
        # [discussion](https://github.com/plone/plone.restapi/pull/1141#discussion_r648843942)
        # we opt for the latter.
        login_view = component.getMultiAdapter(
            (self.context, self.request),
            name="login",
        )
        login_view._post_login()

        payload = {}
        payload["fullname"] = user.getProperty("fullname")
        return TokenOutputDTO(
            token=plugin.create_token(user.getId(), data=payload)
        ).dict()

    def _find_userfolder(self, userid):
        """Try to find a user folder that contains a user with the given
        userid.
        """
        uf_parent = aq_inner(self.context)
        info = None

        while not info:
            uf = getToolByName(uf_parent, "acl_users")
            if uf:
                info = uf._verifyUser(uf.plugins, login=userid)
            if uf_parent is self.context.getPhysicalRoot():
                break
            uf_parent = aq_parent(uf_parent)

        if info:
            return uf

    def check_permission(self):
        pass
