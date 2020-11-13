# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFCore.permissions import AddPortalMember
from Products.CMFCore.permissions import SetOwnPassword
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from Products.CMFPlone.utils import getFSVersionTuple
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import plone.protect.interfaces
import six


try:  # pragma: no cover
    from Products.CMFPlone.interfaces import ISecuritySchema
except ImportError:  # pragma: no cover
    from plone.app.controlpanel.security import ISecuritySchema

try:  # pragma: no cover
    # Plone 5.1+
    from Products.CMFPlone.PasswordResetTool import ExpiredRequestError
    from Products.CMFPlone.PasswordResetTool import InvalidRequestError
except ImportError:  # pragma: no cover
    # Plone 5.0 and earlier
    from Products.PasswordResetTool.PasswordResetTool import ExpiredRequestError  # noqa
    from Products.PasswordResetTool.PasswordResetTool import InvalidRequestError  # noqa

PLONE5 = getFSVersionTuple()[0] >= 5


@implementer(IPublishTraverse)
class UsersPost(Service):
    """Creates a new user."""

    def __init__(self, context, request):
        super(UsersPost, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    def validate_input_data(self, portal, original_data):
        """Returns a tuple of (required_fields, allowed_fields)"""
        security = getAdapter(portal, ISecuritySchema)

        # remove data we don't want to check for
        data = {}
        for key in ["username", "email", "password", "roles", "sendPasswordReset"]:
            if key in original_data:
                data[key] = original_data[key]

        required = ["email"]
        allowed = ["email"]

        if not security.use_email_as_login:
            required.append("username")
            allowed.append("username")

        if self.can_manage_users:
            allowed.append("password")
            allowed.append("sendPasswordReset")
            allowed.append("roles")
        else:
            if security.enable_user_pwd_choice:
                allowed.append("password")
                required.append("password")

        # check input data
        for fieldname in required:
            if not data.get(fieldname, None):
                self.add_field_error(
                    fieldname, "Property '{}' is required.".format(fieldname)
                )
        for fieldname in data:
            if fieldname not in allowed:
                self.add_field_error(
                    fieldname, "Property '{}' is not allowed.".format(fieldname)
                )

        password = data.get("password")
        send_password_reset = data.get("sendPasswordReset")
        if self.can_manage_users:
            if password is None and send_password_reset is None:
                self.add_field_error(
                    "sendPasswordReset",
                    "You have to either send a password or sendPasswordReset.",
                )
            if password and send_password_reset:
                self.add_field_error(
                    "sendPasswordReset",
                    "You can't send both password and sendPasswordReset.",
                )

    def add_field_error(self, field, message):
        self.errors.append({"field": field, "message": message})

    def errors_to_string(self):
        return " ".join([error["message"] for error in self.errors])

    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        portal = getSite()

        # validate important data
        data = json_body(self.request)
        self.errors = []
        self.validate_input_data(portal, data)
        security = getAdapter(self.context, ISecuritySchema)
        registration = getToolByName(self.context, "portal_registration")

        general_usage_error = (
            "Either post to @users to create a user or use "
            "@users/<username>/reset-password to update the password."
        )
        if len(self.params) not in [0, 2]:
            raise Exception(general_usage_error)

        if len(self.params) == 2:
            if self.params[1] == "reset-password":
                return self.update_password(data)
            raise Exception("Unknown Endpoint @users/%s/%s" % self.params)

        # Add a portal member
        if not self.can_add_member:
            return self._error(403, "Forbidden", "You need AddPortalMember permission.")

        if self.errors:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="WrongParameterError",
                    message="Error in fields. {}".format(self.errors_to_string()),
                    errors=self.errors,
                )
            )

        username = data.pop("username", None)
        email = data.pop("email", None)
        password = data.pop("password", None)
        roles = data.pop("roles", ["Member"])
        send_password_reset = data.pop("sendPasswordReset", None)
        properties = data

        if PLONE5:
            # We are improving the way the userid/login_name is generated using
            # Plone's plone.app.users utilities directly. Plone 4 lacks of the
            # login_name one, so we leave it as it is, improving the Plone 5
            # story
            user_id_login_name_data = {
                "username": username,
                "email": email,
                "fullname": data.get("fullname", ""),
            }

            register_view = getMultiAdapter(
                (self.context, self.request), name="register"
            )

            register_view.generate_user_id(user_id_login_name_data)
            register_view.generate_login_name(user_id_login_name_data)

            user_id = user_id_login_name_data.get("user_id", data.get("username"))
            login_name = user_id_login_name_data.get("login_name", data.get("username"))

            username = user_id
            properties["username"] = user_id
        else:
            # set username based on the login settings (username or email)
            if security.use_email_as_login:
                username = email
                properties["username"] = email
            else:
                properties["username"] = username

        properties["email"] = email

        if not self.can_manage_users and not security.enable_user_pwd_choice:
            send_password_reset = True
        if send_password_reset:
            password = registration.generatePassword()
        # Create user
        try:
            registration = getToolByName(portal, "portal_registration")
            user = registration.addMember(
                username, password, roles, properties=properties
            )
        except ValueError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type="MissingParameterError", message=str(e)))

        if PLONE5:
            # After user creation, we have to fix the login_name if it differs.
            # That happens when the email login is enabled and we are using
            # UUID as user ID security settings.
            if user_id != login_name:
                # The user id differs from the login name.  Set the login
                # name correctly.
                pas = getToolByName(self.context, "acl_users")
                pas.updateLoginName(user_id, login_name)

        if send_password_reset:
            registration.registeredNotify(username)
        self.request.response.setStatus(201)
        # Note: to please Zope 4.5.2+ we make sure the header is a string,
        # and not unicode on Python 2.
        if six.PY2 and not isinstance(username, str):
            username = username.encode("utf-8")
        self.request.response.setHeader(
            "Location", portal.absolute_url() + "/@users/" + username
        )
        serializer = queryMultiAdapter((user, self.request), ISerializeToJson)
        return serializer()

    def _get_user(self, user_id):
        portal = getSite()
        portal_membership = getToolByName(portal, "portal_membership")
        return portal_membership.getMemberById(user_id)

    def _get_user_by_login_name(self, user_id):
        return get_member_by_login_name(self.context, user_id, raise_exceptions=False)

    def _error(self, status, type, message):
        self.request.response.setStatus(status)
        return {"error": {"type": type, "message": message}}

    @property
    def can_manage_users(self):
        sm = getSecurityManager()
        return sm.checkPermission("plone.app.controlpanel.UsersAndGroups", self.context)

    @property
    def can_set_own_password(self):
        sm = getSecurityManager()
        return sm.checkPermission(SetOwnPassword, self.context)

    @property
    def can_add_member(self):
        sm = getSecurityManager()
        return sm.checkPermission(AddPortalMember, self.context)

    def update_password(self, data):
        username = self.params[0]
        target_user = self._get_user_by_login_name(username)
        reset_token = data.get("reset_token", None)
        old_password = data.get("old_password", None)
        new_password = data.get("new_password", None)

        pas = getToolByName(self.context, "acl_users")
        mt = getToolByName(self.context, "portal_membership")
        pwt = getToolByName(self.context, "portal_password_reset")

        if target_user is None:
            self.request.response.setStatus(404)
            return

        # Send password reset mail
        if list(data) == []:
            registration_tool = getToolByName(self.context, "portal_registration")
            registration_tool.mailPassword(username, self.request)
            return

        if reset_token and old_password:
            return self._error(
                400,
                "Invalid parameters",
                "You can't use 'reset_token' and 'old_password' together.",
            )
        if reset_token and not new_password:
            return self._error(
                400,
                "Invalid parameters",
                "If you pass 'reset_token' you have to pass 'new_password'",
            )
        if old_password and not new_password:
            return self._error(
                400,
                "Invalid parameters",
                "If you pass 'old_password' you have to pass 'new_password'",
            )

        # Reset the password with a reset token
        if reset_token:
            try:
                pwt.resetPassword(username, reset_token, new_password)
            except InvalidRequestError:
                return self._error(
                    403, "Unknown Token", "The reset_token is unknown/not valid."
                )
            except ExpiredRequestError:
                return self._error(403, "Expired Token", "The reset_token is expired.")
            return

        # set the new password by giving the old password
        if old_password:
            if not (self.can_manage_users or self.can_set_own_password):
                return self._error(
                    403,
                    "Not allowed",
                    "You can't set a password without " "a password reset token.",
                )
            authenticated_user_id = mt.getAuthenticatedMember().getId()
            if username != authenticated_user_id:
                return self._error(
                    403,
                    "Wrong user",
                    (
                        "You need to be logged in as the user '%s' to set "
                        "the password."
                    )
                    % username,
                )

            check_password_auth = pas.authenticate(
                username, old_password.encode("utf-8"), self.request
            )
            if not check_password_auth:
                return self._error(
                    403,
                    "Wrong password",
                    "The password passed as 'old_password' " "is wrong.",
                )
            mt.setPassword(new_password)
            return

        return self._error(
            400,
            "Invalid parameters",
            "See the user endpoint documentation for the " "valid parameters.",
        )
