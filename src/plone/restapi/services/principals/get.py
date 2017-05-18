# -*- coding: utf-8 -*-
from itertools import chain
from plone.app.workflow.browser.sharing import merge_search_results
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component import getMultiAdapter


class PrincipalsGet(Service):

    def reply(self):
        if self.request.form.get('search', False):
            self.search_term = self.request.form['search']
        else:
            raise BadRequest('Required \"search\" parameter is missing.')

        users = self.serialize_principals(self.user_search_results())
        groups = self.serialize_principals(self.group_search_results())

        principals = dict(users=users, groups=groups)

        return principals

    def serialize_principals(self, principals):
        result = []
        for principal in principals:
            serializer = getMultiAdapter(
                (principal, self.request),
                ISerializeToJsonSummary
            )
            result.append(serializer())
        return result

    def user_search_results(self):
        def search_for_principal(hunter, search_term):
            return merge_search_results(
                chain(*[hunter.searchUsers(**{field: search_term})
                      for field in ['name', 'fullname', 'email']]), 'userid')

        def get_principal_by_id(user_id):
            mtool = getToolByName(self.context, 'portal_membership')
            return mtool.getMemberById(user_id)

        return self._principal_search_results(
            search_for_principal, get_principal_by_id, 'user', 'userid')

    def group_search_results(self):
        def search_for_principal(hunter, search_term):
            return merge_search_results(
                chain(*[hunter.searchGroups(**{field: search_term})
                      for field in ['id', 'title']]), 'groupid')

        def get_principal_by_id(group_id):
            portal_groups = getToolByName(self.context, 'portal_groups')
            return portal_groups.getGroupById(group_id)

        return self._principal_search_results(
            search_for_principal, get_principal_by_id, 'group', 'groupid')

    def _principal_search_results(
            self, search_for_principal,
            get_principal_by_id,
            principal_type,
            id_key):

        hunter = getMultiAdapter(
            (self.context, self.request), name='pas_search')

        principals = []
        for principal_info in search_for_principal(hunter, self.search_term):
            principal_id = principal_info[id_key]
            principals.append(get_principal_by_id(principal_id))

        return principals
