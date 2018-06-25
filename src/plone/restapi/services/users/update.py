# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from plone.restapi.services import Service
from Products.CMFCore.permissions import SetOwnPassword
from Products.CMFPlone.utils import set_own_login_name
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.component import getAdapter

import json
import plone

try:  # pragma: no cover
    from Products.CMFPlone.interfaces import ISecuritySchema
except ImportError:   # pragma: no cover
    from plone.app.controlpanel.security import ISecuritySchema


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
        portal_membership = getToolByName(portal, 'portal_membership')
        return portal_membership.getMemberById(user_id)

    def _change_user_password(self, user, value):
        acl_users = getToolByName(self.context, 'acl_users')
        acl_users.userSetPassword(user.getUserId(), value)

    def reply(self):
        user_settings_to_update = json.loads(self.request.get('BODY', '{}'))
        user = self._get_user(self._get_user_id)

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        security = getAdapter(self.context, ISecuritySchema)

        if self.can_manage_users:
            for key, value in user_settings_to_update.items():
                if key == 'password':
                    self._change_user_password(user, value)
                elif key == 'username':
                    set_own_login_name(user, value)
                else:
                    user.setMemberProperties(mapping={key: value})

            roles = user_settings_to_update.get('roles', {})
            if roles:
                to_add = [key for key, enabled in roles.items() if enabled]
                to_remove = [key for key, enabled in roles.items()
                             if not enabled]

                target_roles = set(user.getRoles()) - set(to_remove)
                target_roles = target_roles | set(to_add)

                acl_users = getToolByName(self.context, 'acl_users')
                acl_users.userFolderEditUser(
                    principal_id=user.id,
                    password=None,
                    roles=target_roles,
                    domains=user.getDomains(),
                )
        elif self._get_current_user == self._get_user_id:
            for key, value in user_settings_to_update.items():
                if key == 'password' and \
                   security.enable_user_pwd_choice and \
                   self.can_set_own_password:
                    self._change_user_password(user, value)
                else:
                    user.setMemberProperties(mapping={key: value})

        else:
            if self._is_anonymous:
                return self._error(401, 'Unauthorized',
                                   'You are not authorized to perform this '
                                   'action')
            else:
                return self._error(403, 'Forbidden', 'You can\'t update the '
                                        'properties of this user')

        self.request.response.setStatus(204)
        return None

    @property
    def can_manage_users(self):
        sm = getSecurityManager()
        return sm.checkPermission('plone.app.controlpanel.UsersAndGroups',
                                  self.context)

    @property
    def can_set_own_password(self):
        sm = getSecurityManager()
        return sm.checkPermission(SetOwnPassword, self.context)

    def _error(self, status, type, message):
        self.request.response.setStatus(status)
        return {'error': {'type': type,
                          'message': message}}

    @property
    def _get_current_user(self):
        portal = getSite()
        portal_membership = getToolByName(portal, 'portal_membership')
        return portal_membership.getAuthenticatedMember().getId()

    @property
    def _is_anonymous(self):
        portal = getSite()
        portal_membership = getToolByName(portal, 'portal_membership')
        return portal_membership.isAnonymousUser()
