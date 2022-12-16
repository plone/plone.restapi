from AccessControl import getSecurityManager
from Acquisition import aq_inner
from io import BytesIO
from OFS.Image import Image
from plone.restapi import _
from plone.restapi.services import Service
from Products.CMFCore.permissions import SetOwnPassword
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.CMFPlone.utils import set_own_login_name
from Products.PlonePAS.tools.membership import default_portrait
from Products.PlonePAS.utils import scale_image
from zope.component import getAdapter
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import codecs
import json
import plone


@implementer(IPublishTraverse)
class UsersPatch(Service):
    """Updates an existing user."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    @property
    def _get_user_id(self):
        if len(self.params) != 1:
            raise Exception("Must supply exactly one parameter (user id)")
        return self.params[0]

    def _get_user(self, user_id):
        portal = getSite()
        portal_membership = getToolByName(portal, "portal_membership")
        return portal_membership.getMemberById(user_id)

    def _change_user_password(self, user, value):
        acl_users = getToolByName(self.context, "acl_users")
        acl_users.userSetPassword(user.getUserId(), value)

    def translate(self, msgid):
        return translate(
            msgid,
            context=self.request,
        )

    def reply(self):
        user_settings_to_update = json.loads(self.request.get("BODY", "{}"))
        user = self._get_user(self._get_user_id)

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        security = getAdapter(self.context, ISecuritySchema)

        if self.can_manage_users:
            for key, value in user_settings_to_update.items():
                if key == "password":
                    self._change_user_password(user, value)
                elif key == "username":
                    set_own_login_name(user, value)
                else:
                    # If the portrait is already set but has not been changed change it,
                    # then the serialized value comes again in the request as a string,
                    # no data on it, then we should not set it since it will fail
                    if key == "portrait" and isinstance(value, dict):
                        self.set_member_portrait(user, value)
                    user.setMemberProperties(mapping={key: value}, force_empty=True)

            roles = user_settings_to_update.get("roles", {})
            if roles:
                to_add = [key for key, enabled in roles.items() if enabled]
                to_remove = [key for key, enabled in roles.items() if not enabled]

                target_roles = set(user.getRoles()) - set(to_remove)
                target_roles = target_roles | set(to_add)

                acl_users = getToolByName(self.context, "acl_users")
                acl_users.userFolderEditUser(
                    principal_id=user.id,
                    password=None,
                    roles=target_roles,
                    domains=user.getDomains(),
                )
        elif self._get_current_user == self._get_user_id:
            for key, value in user_settings_to_update.items():
                if (
                    key == "password"
                    and security.enable_user_pwd_choice
                    and self.can_set_own_password
                ):
                    self._change_user_password(user, value)
                else:
                    # If the portrait is already set but has not been changed change it,
                    # then the serialized value comes again in the request as a string,
                    # no data on it, then we should not set it since it will fail
                    if key == "portrait" and isinstance(value, dict):
                        self.set_member_portrait(user, value)
                    user.setMemberProperties(mapping={key: value}, force_empty=True)

        else:
            if self._is_anonymous:
                return self._error(
                    401,
                    "Unauthorized",
                    _("You are not authorized to perform this action"),
                )
            else:
                return self._error(
                    403,
                    "Forbidden",
                    _("You can't update the properties of this user"),
                )

        return self.reply_no_content()

    @property
    def can_manage_users(self):
        sm = getSecurityManager()
        return sm.checkPermission("plone.app.controlpanel.UsersAndGroups", self.context)

    @property
    def can_set_own_password(self):
        sm = getSecurityManager()
        return sm.checkPermission(SetOwnPassword, self.context)

    def _error(self, status, _type, msgid):
        self.request.response.setStatus(status)
        return {"error": {"type": _type, "message": self.translate(msgid)}}

    @property
    def _get_current_user(self):
        portal = getSite()
        portal_membership = getToolByName(portal, "portal_membership")
        return portal_membership.getAuthenticatedMember().getId()

    @property
    def _is_anonymous(self):
        portal = getSite()
        portal_membership = getToolByName(portal, "portal_membership")
        return portal_membership.isAnonymousUser()

    def set_member_portrait(self, user, portrait):
        portal = getSite()
        portal_membership = getToolByName(portal, "portal_membership")
        safe_id = portal_membership._getSafeMemberId(user.getId())

        if portrait is None:
            previous = portal_membership.getPersonalPortrait(safe_id)
            default_portrait_value = getattr(portal, default_portrait, None)
            if aq_inner(previous) != aq_inner(default_portrait_value):
                portal_membership.deletePersonalPortrait(str(safe_id))
            return

        content_type = "application/octet-stream"
        filename = None

        content_type = portrait.get("content-type", content_type)
        filename = portrait.get("filename", filename)
        data = portrait.get("data")
        if isinstance(data, str):
            data = data.encode("utf-8")
        if "encoding" in portrait:
            data = codecs.decode(data, portrait["encoding"])

        if portrait.get("scale", False):
            # Only scale if the scale (default Plone behavior) boolean is set
            # This should be handled by the core in the future
            scaled, _mimetype = scale_image(BytesIO(data))
        else:
            # Normally, the scale and cropping is going to be handled in the
            # frontend
            scaled = data

        portrait = Image(id=safe_id, file=scaled, title="")
        membertool = getToolByName(self, "portal_memberdata")
        membertool._setPortrait(portrait, safe_id)
