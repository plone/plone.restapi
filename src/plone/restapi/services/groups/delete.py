# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import NotFound
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class GroupsDelete(Service):
    """Deletes a user."""

    def __init__(self, context, request):
        super(GroupsDelete, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@groups as parameters
        self.params.append(name)
        return self

    @property
    def _get_group_id(self):
        if len(self.params) != 1:
            raise Exception("Must supply exactly one parameter (group id)")
        return self.params[0]

    def _get_group(self, group_id):
        portal = getSite()
        portal_groups = getToolByName(portal, "portal_groups")
        return portal_groups.getGroupById(group_id)

    def reply(self):

        portal_groups = getToolByName(self.context, "portal_groups")
        group = self._get_group(self._get_group_id)

        if not group:
            raise NotFound("Trying to delete a non-existing group.")

        delete_successful = portal_groups.removeGroup(self._get_group_id)
        if delete_successful:
            return self.reply_no_content()
        else:
            return self.reply_no_content(status=404)
