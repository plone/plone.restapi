# -*- coding: utf-8 -*-
from plone import api
from plone.api.exc import MissingParameterError
from plone.api.exc import InvalidParameterError
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter
from zExceptions import BadRequest
from zope.interface import alsoProvides

import plone.protect.interfaces


class UsersPost(Service):
    """Creates a new user.
    """

    def reply(self):
        data = json_body(self.request)

        username = data.get('username', None)
        email = data.get('email', None)
        password = data.get('password', None)
        roles = data.get('roles', [])
        properties = data.get('properties', {})

        if not username:
            raise BadRequest("Property 'username' is required")

        if not email:
            raise BadRequest("Property 'email' is required")

        if not password:
            raise BadRequest("Property 'password' is required")

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        # Create user
        try:
            user = api.user.create(
                email=email,
                username=username,
                password=password,
                roles=roles,
                properties=properties
            )
        except MissingParameterError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='MissingParameterError',
                message=str(e.message)))
        except InvalidParameterError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='InvalidParameterError',
                message=str(e.message)))

        self.request.response.setStatus(201)
        self.request.response.setHeader(
            'Location', api.portal.get().absolute_url() + '/@users/' + username
        )
        serializer = queryMultiAdapter(
            (user, self.request),
            ISerializeToJson
        )
        return serializer()
