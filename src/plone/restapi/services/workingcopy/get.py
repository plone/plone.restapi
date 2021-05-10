# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.permissions import CheckoutPermission
from plone.restapi.services import Service
from Products.CMFCore.permissions import ModifyPortalContent


class GetWorkingCopy(Service):
    def reply(self):
        sm = getSecurityManager()
        policy = ICheckinCheckoutPolicy(self.context)
        working_copy = policy.getWorkingCopy()

        if (
            sm.checkPermission(ModifyPortalContent, self.context)
            or sm.checkPermission(CheckoutPermission, self.context)
            or sm.checkPermission(ModifyPortalContent, working_copy)
        ):
            if working_copy is not None:
                return {"@id": working_copy.absolute_url()}
            else:
                return None
        else:
            return self._error(
                403, "Not authorized", "Get info of working copy not allowed"
            )

    def _error(self, status, type, message):
        self.request.response.setStatus(status)
        return {"error": {"type": type, "message": message}}
