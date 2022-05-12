from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class UsersDelete(Service):
    """Deletes a user."""

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

    def reply(self):
        portal = getSite()
        portal_membership = getToolByName(portal, "portal_membership")
        delete_successful = portal_membership.deleteMembers((self._get_user_id,))
        if delete_successful:
            return self.reply_no_content()
        else:
            return self.reply_no_content(status=404)
