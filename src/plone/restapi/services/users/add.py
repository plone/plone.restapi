from AccessControl import getSecurityManager
from plone.app.users.schema import ICombinedRegisterSchema
from plone.restapi import _
from plone.restapi.bbb import ISecuritySchema
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFCore.permissions import AddPortalMember
from Products.CMFCore.permissions import SetOwnPassword
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PasswordResetTool import ExpiredRequestError
from Products.CMFPlone.PasswordResetTool import InvalidRequestError
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import plone.protect.interfaces


@implementer(IPublishTraverse)
class UsersPost(Service):
    """Creates a new user."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    def translate(self, msgid):
        return translate(
            msgid,
            context=self.request,
        )

    def translate_fieldname(self, fieldname):
        """Not all fields that appear on Add User Form in Volto match in Plone."""
        if fieldname == "roles":
            msgid = _("Roles")
        elif fieldname == "sendPasswordReset":
            msgid = ICombinedRegisterSchema["mail_me"].title
        else:
            msgid = ICombinedRegisterSchema[fieldname].title
        return self.translate(msgid)

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
                translated_fieldname = self.translate_fieldname(fieldname)
                self.add_field_error(
                    fieldname,
                    _(
                        "Property '${fieldname}' is required.",
                        mapping={"fieldname": translated_fieldname},
                    ),
                )
        for fieldname in data:
            if fieldname not in allowed:
                translated_fieldname = self.translate_fieldname(fieldname)
                self.add_field_error(
                    fieldname,
                    _(
                        "Property '${fieldname}' is not allowed.",
                        mapping={"fieldname": translated_fieldname},
                    ),
                )

        password = data.get("password")
        send_password_reset = data.get("sendPasswordReset")
        if self.can_manage_users:
            if password is None and send_password_reset is None:
                self.add_field_error(
                    "sendPasswordReset",
                    _("You have to either send a password or sendPasswordReset."),
                )
            if password and send_password_reset:
                self.add_field_error(
                    "sendPasswordReset",
                    _("You can't send both password and sendPasswordReset."),
                )

    def add_field_error(self, field, msgid):
        self.errors.append({"field": field, "message": self.translate(msgid)})

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
            return self._error(
                403,
                "Forbidden",
                _("You need AddPortalMember permission."),
            )

        if self.errors:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="WrongParameterError",
                    message=self.translate(
                        _(
                            "Error in fields. ${errors_to_string}",
                            mapping={"errors_to_string": self.errors_to_string()},
                        )
                    ),
                    errors=self.errors,
                )
            )

        username = data.pop("username", None)
        email = data.pop("email", None)
        password = data.pop("password", None)
        roles = data.pop("roles", ["Member"])
        send_password_reset = data.pop("sendPasswordReset", None)
        properties = data

        user_id_login_name_data = {
            "username": username,
            "email": email,
            "fullname": data.get("fullname", ""),
        }

        register_view = getMultiAdapter((self.context, self.request), name="register")

        register_view.generate_user_id(user_id_login_name_data)
        register_view.generate_login_name(user_id_login_name_data)

        user_id = user_id_login_name_data.get("user_id", data.get("username"))
        login_name = user_id_login_name_data.get("login_name", data.get("username"))

        username = user_id
        properties["username"] = user_id

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
            return dict(
                error=dict(
                    type="MissingParameterError",
                    message=self.translate(e.args[0]),
                )
            )

        if user_id != login_name:
            # The user id differs from the login name.  Set the login
            # name correctly.
            pas = getToolByName(self.context, "acl_users")
            pas.updateLoginName(user_id, login_name)

        if send_password_reset:
            registration.registeredNotify(username)
        self.request.response.setStatus(201)
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

    def _error(self, status, _type, msgid):
        self.request.response.setStatus(status)
        return {"error": {"type": _type, "message": self.translate(msgid)}}

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
        registration_tool = getToolByName(self.context, "portal_registration")

        if target_user is None:
            self.request.response.setStatus(404)
            return

        # Send password reset mail
        if list(data) == []:
            registration_tool.mailPassword(username, self.request)
            return

        if reset_token and old_password:
            return self._error(
                400,
                "Invalid parameters",
                _("You can't use 'reset_token' and 'old_password' together."),
            )
        if reset_token and not new_password:
            return self._error(
                400,
                "Invalid parameters",
                _("If you pass 'reset_token' you have to pass 'new_password'"),
            )
        if old_password and not new_password:
            return self._error(
                400,
                "Invalid parameters",
                _("If you pass 'old_password' you have to pass 'new_password'"),
            )

        # Reset the password with a reset token
        if reset_token:
            try:
                err = registration_tool.testPasswordValidity(new_password)
                if err is not None:
                    return self._error(
                        400,
                        "Invalid password",
                        _(err),
                    )
                pwt.resetPassword(username, reset_token, new_password)
            except InvalidRequestError:
                return self._error(
                    403,
                    "Unknown Token",
                    _("The reset_token is unknown/not valid."),
                )
            except ExpiredRequestError:
                return self._error(
                    403,
                    _("Expired Token", "The reset_token is expired."),
                )
            return

        # set the new password by giving the old password
        if old_password:
            if not (self.can_manage_users or self.can_set_own_password):
                return self._error(
                    403,
                    "Not allowed",
                    _("You can't set a password without a password reset token."),
                )
            authenticated_user_id = mt.getAuthenticatedMember().getId()
            if username != authenticated_user_id:
                return self._error(
                    403,
                    "Wrong user",
                    _(
                        "You need to be logged in as the user '${username}' to set the password.",
                        mapping={"username": username},
                    ),
                )

            check_password_auth = pas.authenticate(
                username, old_password.encode("utf-8"), self.request
            )
            if not check_password_auth:
                return self._error(
                    403,
                    "Wrong password",
                    _("The password passed as 'old_password' is wrong."),
                )
            mt.setPassword(new_password)
            return

        return self._error(
            400,
            "Invalid parameters",
            _("See the user endpoint documentation for the valid parameters."),
        )
