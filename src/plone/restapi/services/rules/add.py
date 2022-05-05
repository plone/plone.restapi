from plone.app.contentrules.browser.assignments import ManageAssignments
from plone.restapi.services import Service
import plone.protect.interfaces
from zope.interface import implementer
from zope.interface import alsoProvides
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class RulesAdd(Service):
    """Adds rules"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@rules as parameters
        self.params.append(name)
        return self

    def reply(self):

        if not self.params:
            raise BadRequest("Missing parameter typename")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        import ipdb;ipdb.set_trace()
        manage_assignments = ManageAssignments(self.context, self.request)
        acquired_rules = manage_assignments.acquired_rules()
        assigned_rules = manage_assignments.assigned_rules()

        return {
            "rules": {
                "acquired_rules": acquired_rules,
                "assigned_rules": assigned_rules
                }
        }
