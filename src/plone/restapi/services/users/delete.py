from AccessControl import getSecurityManager
from plone.restapi.services import Service
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component import getUtility
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
        self.acl_users = getToolByName(context, "acl_users")

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
        user = self._get_user(self._get_user_id)
        if not user:
            return self.reply_no_content(status=404)
        if not self.is_zope_manager:
            current_roles = user.getRoles()
            if "Manager" in current_roles:
                raise BadRequest(
                    "You don't have permission to delete a user with 'Manager' role."
                )

        delete_memberareas = (
            self.request.get("delete_memberareas", True) not in FALSE_VALUES
        )

        delete_localroles = (
            self.request.get("delete_localroles", True) not in FALSE_VALUES
        )

        try:
            self.acl_users.userFolderDelUsers((self._get_user_id,))
        except (AttributeError, NotImplementedError):
            return self.reply_no_content(status=404)

        if delete_memberareas:
            # Delete member data in portal_memberdata.
            mdtool = getToolByName(self.context, "portal_memberdata", None)
            if mdtool is not None:
                mdtool.deleteMemberData(self._get_user_id)

        if delete_localroles:
            # Delete members' local roles.
            self.portal_membership.deleteLocalRoles(
                getUtility(ISiteRoot), (self._get_user_id,), reindex=1, recursive=1
            )

        return self.reply_no_content()
