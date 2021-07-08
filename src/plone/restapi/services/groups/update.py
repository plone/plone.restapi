from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import plone


@implementer(IPublishTraverse)
class GroupsPatch(Service):
    """Updates an existing group."""

    def __init__(self, context, request):
        super().__init__(context, request)
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
        data = json_body(self.request)
        group = self._get_group(self._get_group_id)

        if not group:
            raise BadRequest("Trying to update a non-existing group.")

        title = data.get("title", None)
        description = data.get("description", None)
        roles = data.get("roles", None)
        groups = data.get("groups", None)
        users = data.get("users", {})

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        portal_groups = getToolByName(self.context, "portal_groups")

        portal_groups.editGroup(
            self._get_group_id,
            roles=roles,
            groups=groups,
            title=title,
            description=description,
        )

        properties = {}
        for id, property in group.propertyItems():
            if data.get(id, False):
                properties[id] = data[id]

        group.setGroupProperties(properties)

        # Add/remove members
        memberids = group.getGroupMemberIds()
        for userid, allow in users.items():
            if allow:
                if userid not in memberids:
                    group.addMember(userid)
            else:
                if userid in memberids:
                    group.removeMember(userid)

        return self.reply_no_content()
