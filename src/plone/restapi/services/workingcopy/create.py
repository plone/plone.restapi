from plone.restapi.services import Service
from zope.interface import alsoProvides
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import IWCContainerLocator
from Acquisition import aq_inner
from zope.component import getAdapters
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

import plone.protect.interfaces

# It seems that p.a.iterate allows to locate the WC in the user folder,
# for now, ignore it and use always the location as the parent
# but allow space to implement it in the future if it's still relevant
WC_LOCATION_MODE = "plone.app.iterate.parent"


class CreateWorkingCopy(Service):
    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        control = getMultiAdapter((self.context, self.request), name="iterate_control")
        if not control.checkout_allowed():
            pm = getToolByName(self.context, "portal_membership")
            if bool(pm.isAnonymousUser()):
                return self._error(401, "Not authenticated", "Checkout not allowed")
            else:
                return self._error(403, "Not authorized", "Checkout not allowed")

        locator = None
        try:
            locator = [
                c["locator"] for c in self.containers() if c["name"] == WC_LOCATION_MODE
            ][0]
        except IndexError:
            return self._error(
                500, "InternalServerError", "Cannot find checkout location"
            )

        policy = ICheckinCheckoutPolicy(self.context)
        wc = policy.checkout(locator())

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", self.context.absolute_url())
        return {"@id": wc.absolute_url()}

    def containers(self):
        """Get a list of potential containers (copied over from p.a.iterate)"""
        context = aq_inner(self.context)
        for name, locator in getAdapters((context,), IWCContainerLocator):
            if locator.available:
                yield dict(name=name, locator=locator)

    def _error(self, status, type, message):
        self.request.response.setStatus(status)
        return {"error": {"type": type, "message": message}}
