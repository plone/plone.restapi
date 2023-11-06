from AccessControl import getSecurityManager
from Acquisition import aq_inner
from plone.restapi.services import Service
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate


class RolesGet(Service):
    @property
    def is_zope_manager(self):
        return getSecurityManager().checkPermission(ManagePortal, self.context)

    def can_assign(self, is_zope_manager, _id):
        if is_zope_manager:
            return True
        return _id != "Manager"

    def reply(self):
        pmemb = getToolByName(aq_inner(self.context), "portal_membership")
        roles = [r for r in pmemb.getPortalRoles() if r != "Owner"]
        is_zope_manager = self.is_zope_manager
        return [
            {
                "@type": "role",
                "@id": f"{self.context.absolute_url()}/@roles/{r}",
                "id": r,
                "title": translate(r, context=self.request, domain="plone"),
                "can_assign": self.can_assign(is_zope_manager, r),
            }
            for r in roles
        ]
