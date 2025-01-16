from AccessControl import getSecurityManager
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import alsoProvides

import plone.protect.interfaces


class GroupsPost(Service):
    """Creates a new group."""

    @property
    def is_zope_manager(self):
        return getSecurityManager().checkPermission(ManagePortal, self.context)

    def reply(self):
        portal = getSite()
        data = json_body(self.request)

        groupname = data.get("groupname", None)

        if not groupname:
            raise BadRequest("Property 'groupname' is required")

        roles = data.get("roles", [])

        if not self.is_zope_manager and "Manager" in roles:
            raise BadRequest(
                "You don't have permission to create a group with the 'Manager' role"
            )

        email = data.get("email", None)
        title = data.get("title", None)
        description = data.get("description", None)
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
            gtool.addPrincipalToGroup(userid, groupname)

        self.request.response.setStatus(201)
        self.request.response.setHeader(
            "Location", portal.absolute_url() + "/@groups/" + groupname
        )
        serializer = queryMultiAdapter((group, self.request), ISerializeToJson)
        return serializer()
