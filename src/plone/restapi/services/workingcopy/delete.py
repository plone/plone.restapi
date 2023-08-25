from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.restapi.services import Service
from zope.component import getMultiAdapter


class DeleteWorkingCopy(Service):
    def reply(self):
        policy = ICheckinCheckoutPolicy(self.context)
        working_copy = policy.getWorkingCopy()
        if not policy.getBaseline():
            # We are in the baseline, get the working copy policy
            policy = ICheckinCheckoutPolicy(working_copy)

        control = getMultiAdapter((working_copy, self.request), name="iterate_control")

        if not control.cancel_allowed():
            return self._error(403, "Not authorized", "Cancel not allowed")

        baseline = policy.cancelCheckout()
        baseline.reindexObject()

        return self.reply_no_content()

    def _error(self, status, type, message):
        self.request.response.setStatus(status)
        return {"error": {"type": type, "message": message}}
