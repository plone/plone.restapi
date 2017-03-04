# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapter
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import alsoProvides

import plone.protect.interfaces

try:
    from Products.CMFPlone.interfaces import ISecuritySchema
except ImportError:
    from plone.app.controlpanel.security import ISecuritySchema


class UsersPost(Service):
    """Creates a new user.
    """

    def validate_input_data(self, portal, data):
        '''Returns a tuple of (required_fields, allowed_fields)'''
        security = getAdapter(portal, ISecuritySchema)
        security.use_email_as_login

        required = ['email']
        allowed = ['email']

        if not security.use_email_as_login:
            required.append('username')
            allowed.append('username')

        if self.can_manage_users:
            allowed.append('password')
            allowed.append('sendPasswordReset')
            allowed.append('roles')
        else:
            if security.enable_user_pwd_choice:
                allowed.append('password')
                required.append('password')

        # check input data
        for fieldname in required:
            if not data.get(fieldname, None):
                self.add_field_error(
                    fieldname,
                    'Property \'{}\' is required.'.format(fieldname))
        for fieldname in data:
            if fieldname not in allowed:
                self.add_field_error(
                    fieldname,
                    'Property \'{}\' is not allowed.'.format(fieldname))

        password = data.get('password')
        send_password_reset = data.get('sendPasswordReset')
        if self.can_manage_users:
            if password is None and send_password_reset is None:
                self.add_field_error(
                    'sendPasswordReset',
                    'You have to either send a password or sendPasswordReset.')
            if password and send_password_reset:
                self.add_field_error(
                    'sendPasswordReset',
                    'You can\'t send both password and sendPasswordReset.')

    def add_field_error(self, field, message):
        self.errors.append({'field': field,
                            'message': message})

    def errors_to_string(self):
        return ' '.join([error['message'] for error in self.errors])

    @property
    def can_manage_users(self):
        return api.user.has_permission(
            'plone.app.controlpanel.UsersAndGroups')

    def reply(self):
        portal = getSite()
        data = json_body(self.request)
        self.errors = []
        self.validate_input_data(portal, data)
        security = getAdapter(self.context, ISecuritySchema)
        registration = getToolByName(self.context, 'portal_registration')

        username = data.get('username', None)
        email = data.get('email', None)
        password = data.get('password', None)
        roles = data.get('roles', [])
        properties = data.get('properties', {})
        send_password_reset = data.get('sendPasswordReset', None)

        if self.errors:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='WrongParameterError',
                message='Error in fields. {}'.format(self.errors_to_string()),
                errors=self.errors))

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        # set username based on the login settings (username or email)
        if security.use_email_as_login:
            username = email
            properties['username'] = email
        else:
            properties['username'] = username

        properties['email'] = email

        if not self.can_manage_users and not security.enable_user_pwd_choice:
            send_password_reset = True
        if send_password_reset:
            password = registration.generatePassword()
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

        if send_password_reset:
            registration.registeredNotify(username)
        self.request.response.setStatus(201)
        self.request.response.setHeader(
            'Location', portal.absolute_url() + '/@users/' + username
        )
        serializer = queryMultiAdapter(
            (user, self.request),
            ISerializeToJson
        )
        return serializer()
