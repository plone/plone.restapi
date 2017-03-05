# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from Products.CMFPlone.utils import set_own_login_name
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

import json
import plone.api.portal


class UsersPatch(Service):
    """Updates an existing user.
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(UsersPatch, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    @property
    def _get_user_id(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (user id)")
        return self.params[0]

    def _get_user(self, user_id):
        portal = getSite()
        portal_membership = plone.api.portal.get_tool('portal_membership')
        return portal_membership.getMemberById(user_id)

    def reply(self):
        user_settings_to_update = json.loads(self.request.get('BODY', '{}'))
        user = self._get_user(self._get_user_id)

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        for key, value in user_settings_to_update.items():
            if key == 'password':
                user.userSetPassword(user.getUserId(), value)
            elif key == 'username':
                set_own_login_name(user, value)
            else:
                user.setMemberProperties(mapping={key: value})

        self.request.response.setStatus(204)
        return None
