from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import alsoProvides

import plone.protect.interfaces


class GroupsPost(Service):
    """Creates a new group."""

    def reply(self):
        portal = getSite()
        data = json_body(self.request)

        groupname = data.get("groupname", None)

        if not groupname:
            raise BadRequest("Property 'groupname' is required")

        email = data.get("email", None)
        title = data.get("title", None)
        description = data.get("description", None)
        roles = data.get("roles", None)
        groups = data.get("groups", None)
        users = data.get("users", [])

        properties = {"title": title, "description": description, "email": email}

        gtool = getToolByName(self.context, "portal_groups")
        regtool = getToolByName(self.context, "portal_registration")

        if not regtool.isMemberIdAllowed(groupname):
            raise BadRequest("The group name you entered is not valid.")

        already_exists = gtool.getGroupById(groupname)
        if already_exists:
            raise BadRequest("The group name you entered already exists.")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        success = gtool.addGroup(
            groupname,
            roles,
            groups,
            properties=properties,
            title=title,
            description=description,
        )
        if not success:
            raise BadRequest(f"Error occurred, could not add group {groupname}.")

        # Add members
        group = gtool.getGroupById(groupname)
        for userid in users:
            group.addMember(userid)

        self.request.response.setStatus(201)
        self.request.response.setHeader(
            "Location", portal.absolute_url() + "/@groups/" + groupname
        )
        serializer = queryMultiAdapter((group, self.request), ISerializeToJson)
        return serializer()
