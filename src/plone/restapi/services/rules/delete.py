from plone.app.contentrules.browser.assignments import ManageAssignments
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Rules:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):

        result = {"rules": {"@id": f"{self.context.absolute_url()}/@rules"}}
        if not expand:
            return result

        manage_assignments = ManageAssignments(self.context, self.request)
        acquired_rules = manage_assignments.acquired_rules()
        assigned_rules = manage_assignments.assigned_rules()

        return {
            "rules": {
                "acquired_rules": acquired_rules,
                "assigned_rules": assigned_rules
                }
        }


class RulesDelete(Service):
    def reply(self):
        rules = Rules(self.context, self.request)
        return rules(expand=True)["rules"]
