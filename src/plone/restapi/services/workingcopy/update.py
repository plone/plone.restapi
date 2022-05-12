from plone.restapi.services import Service
from zope.interface import alsoProvides
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

import plone.protect.interfaces


class UpdateWorkingCopy(Service):
    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        policy = ICheckinCheckoutPolicy(self.context)
        working_copy = policy.getWorkingCopy()
        if not policy.getBaseline():
            # We are in the baseline, get the working copy policy
            policy = ICheckinCheckoutPolicy(working_copy)

        control = getMultiAdapter((working_copy, self.request), name="iterate_control")
        if not control.checkin_allowed():
            pm = getToolByName(self.context, "portal_membership")
            if bool(pm.isAnonymousUser()):
                return self._error(401, "Not authenticated", "Checkin not allowed")
            else:
                return self._error(403, "Not authorized", "Checkin not allowed")

        policy.checkin("")

        return self.reply_no_content()

    def _error(self, status, type, message):
        self.request.response.setStatus(status)
        return {"error": {"type": type, "message": message}}
