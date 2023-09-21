from AccessControl import getSecurityManager
from plone.restapi.services import Service
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


FALSE_VALUES = (0, "0", False, "false", "no")


@implementer(IPublishTraverse)
class UsersDelete(Service):
    """Deletes a user."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []
        self.portal_membership = getToolByName(context, "portal_membership")

    @property
    def is_zope_manager(self):
        return getSecurityManager().checkPermission(ManagePortal, self.context)

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
        return self.portal_membership.getMemberById(user_id)

    def reply(self):
        if not self.is_zope_manager:
            user = self._get_user(self._get_user_id)
            current_roles = user.getRoles()
            if "Manager" in current_roles:
                return self.reply_no_content(status=403)

        delete_memberareas = (
            self.request.get("delete_memberareas", True) not in FALSE_VALUES
        )

        delete_localroles = (
            self.request.get("delete_localroles", True) not in FALSE_VALUES
        )

        delete_successful = self.portal_membership.deleteMembers(
            (self._get_user_id,),
            delete_memberareas=delete_memberareas,
            delete_localroles=delete_localroles,
        )
        if delete_successful:
            return self.reply_no_content()
        else:
            return self.reply_no_content(status=404)
