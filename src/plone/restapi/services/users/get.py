# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component.hooks import getSite
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

DEFAULT_SEARCH_RESULTS_LIMIT = 25


class UsersGet(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(UsersGet, self).__init__(context, request)
        self.params = []
        self.query = self.request.form.copy()

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

    def _get_users(self):
        portal = getSite()
        portal_membership = getToolByName(portal, 'portal_membership')
        return portal_membership.listMembers()

    def _get_filtered_users(self, query, limit):
        portal = getSite()
        acl_users = getToolByName(portal, 'acl_users')
        portal_membership = getToolByName(portal, 'portal_membership')
        results = acl_users.searchUsers(id=query, max_results=limit)
        return [portal_membership.getMemberById(user['userid'])
                for user in results]

    def reply(self):
        sm = getSecurityManager()
        if len(self.query) > 0 and len(self.params) == 0:
            query = self.query.get('query', '')
            limit = self.query.get('limit', DEFAULT_SEARCH_RESULTS_LIMIT)
            if query:
                # Someone is searching users, check if he is authorized
                if sm.checkPermission('Manage portal', self.context):
                    users = self._get_filtered_users(query, limit)
                    result = []
                    for user in users:
                        serializer = queryMultiAdapter(
                            (user, self.request),
                            ISerializeToJson
                        )
                        result.append(serializer())
                    return result
                else:
                    self.request.response.setStatus(401)
                    return
            else:
                raise BadRequest("Query string supplied is not valid")

        if len(self.params) == 0:
            # Someone is asking for all users, check if he is authorized
            if sm.checkPermission('Manage portal', self.context):
                result = []
                for user in self._get_users():
                    serializer = queryMultiAdapter(
                        (user, self.request),
                        ISerializeToJson
                    )
                    result.append(serializer())
                return result
            else:
                self.request.response.setStatus(401)
                return

        # Some is asking one user, check if the logged in user is asking
        # his own information or he is a Manager
        mt = getToolByName(self.context, 'portal_membership')
        current_user_id = mt.getAuthenticatedMember().getId()

        if sm.checkPermission('Manage portal', self.context) or \
                (current_user_id and current_user_id == self._get_user_id):

            # we retrieve the user on the user id not the username
            user = self._get_user(self._get_user_id)
            if not user:
                self.request.response.setStatus(404)
                return
            serializer = queryMultiAdapter(
                (user, self.request),
                ISerializeToJson
            )
            return serializer()
        else:
            self.request.response.setStatus(401)
            return
