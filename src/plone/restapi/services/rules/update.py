from plone.app.contentrules.browser.assignments import ManageAssignments
from plone.restapi.services import Service
import plone.protect.interfaces
from zope.interface import implementer
from zope.interface import alsoProvides
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class RulesUpdate(Service):
    """Performs sorting/enable/disable (also on subfolders) of rules"""

    def reply(self):

        data = json_body(self.request)

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        manage_assignments = ManageAssignments(self.context, self.request)
        acquired_rules = manage_assignments.acquired_rules()
        assigned_rules = manage_assignments.assigned_rules()

        return {
            "rules": {
                "acquired_rules": acquired_rules,
                "assigned_rules": assigned_rules
                }
        }
