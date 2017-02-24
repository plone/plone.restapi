# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.PasswordResetTool.PasswordResetTool import ExpiredRequestError
from Products.PasswordResetTool.PasswordResetTool import InvalidRequestError
from zope.component import getAdapter
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import BadRequest
from zope.interface import alsoProvides

import plone.protect.interfaces

try:
    from Products.CMFPlone.interfaces import ISecuritySchema
except ImportError:
    from plone.app.controlpanel.security import ISecuritySchema


class UsersPost(Service):
    """Creates a new user.
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(UsersPost, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    def reply(self):
        portal = getSite()
        data = json_body(self.request)

        general_usage_error = (
            "Either post to @users to create a user or use "
            "@users/<username>/reset-password to update the password.")
        if len(self.params) not in [0, 2]:
            raise Exception(general_usage_error)

        if len(self.params) == 2:
            if self.params[1] == 'reset-password':
                return self.update_password(data)
            raise Exception('Unknown Endpoint @users/%s/%s' % self.params)

        username = data.get('username', None)
        email = data.get('email', None)
        password = data.get('password', None)
        roles = data.get('roles', [])
        properties = data.get('properties', {})

        security_settings = getAdapter(self.context, ISecuritySchema)
        use_email_as_login = security_settings.use_email_as_login

        if not username and not use_email_as_login:
            raise BadRequest("Property 'username' is required")

        if not email and use_email_as_login:
            raise BadRequest("Property 'email' is required")

        if not password:
            raise BadRequest("Property 'password' is required")

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        # set username based on the login settings (username or email)
        if use_email_as_login:
            username = email
            properties['username'] = email
        else:
            properties['username'] = username

        # set email property
        if email:
            properties['email'] = email

        # Create user
        try:
            registration = getToolByName(portal, 'portal_registration')
            user = registration.addMember(
                username,
                password,
                roles,
                properties=properties
            )
        except ValueError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='MissingParameterError',
                message=str(e.message)))

        if not username and use_email_as_login:
            username = email

        self.request.response.setStatus(201)
        self.request.response.setHeader(
            'Location', portal.absolute_url() + '/@users/' + username
        )
        serializer = queryMultiAdapter(
            (user, self.request),
            ISerializeToJson
        )
        return serializer()

    def _get_user(self, user_id):
        portal = getSite()
        portal_membership = getToolByName(portal, 'portal_membership')
        return portal_membership.getMemberById(user_id)

    def _error(self, status, type, message):
        self.request.response.setStatus(status)
        return {'error': {'type': type,
                          'message': message}}

    def update_password(self, data):
        username = self.params[0]
        target_user = self._get_user(username)
        reset_token = data.get('reset_token', None)
        old_password = data.get('old_password', None)
        new_password = data.get('new_password', None)

        pas = getToolByName(self.context, 'acl_users')
        mt = getToolByName(self.context, 'portal_membership')
        pwt = getToolByName(self.context, 'portal_password_reset')

        if target_user is None:
            self.request.response.setStatus(404)
            return

        # Send password reset mail
        if data.keys() == []:
            registration_tool = getToolByName(self.context,
                                              'portal_registration')
            registration_tool.mailPassword(username, self.request)
            return

        if reset_token and old_password:
            return self._error(
                400, 'Invalid parameters',
                "You can't use 'reset_token' and 'old_password' together.")
        if reset_token and not new_password:
            return self._error(
                400, 'Invalid parameters',
                "If you pass 'reset_token' you have to pass 'new_password'")
        if old_password and not new_password:
            return self._error(
                400, 'Invalid parameters',
                "If you pass 'old_password' you have to pass 'new_password'")

        # Reset the password with a reset token
        if reset_token:
            try:
                pwt.resetPassword(username, reset_token, new_password)
            except InvalidRequestError:
                return self._error(403, 'Unknown Token',
                                   'The reset_token is unknown/not valid.')
            except ExpiredRequestError:
                return self._error(403, 'Expired Token',
                                   'The reset_token is expired.')
            return

        if old_password:
            # Check permissions
            # FIXME: Check manager permission
            # FIXME: Check SetOwnPassword Permission
            authenticated_user_id = mt.getAuthenticatedMember().getId()
            if username != authenticated_user_id:
                return self._error(
                    403, "Wrong user"
                    ("You need to be logged in as the user '%s' to set "
                     "the password.") % username)

            check_password_auth = pas.authenticate(
                username, old_password.encode('utf-8'), self.request)
            if not check_password_auth:
                return self._error(403, "Wrong password"
                                   "The password passed as 'old_password' "
                                   "is wrong.")
            mt.setPassword(new_password)
            return

        return self._error(400, 'Invalid parameters',
                           'See the user endpoint documentation for the '
                           'valid parameters.')
