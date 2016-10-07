# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapter
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
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

    def reply(self):
        portal = getSite()
        data = json_body(self.request)

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
