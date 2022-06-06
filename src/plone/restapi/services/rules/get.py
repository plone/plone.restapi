from plone.app.contentrules.browser.assignments import ManageAssignments
from plone.restapi.services import Service


class ContentRulesGet(Service):
    """Publishes the content rules assigned or acquired by given context"""

    def reply(self):
        manage_assignments = ManageAssignments(self.context, self.request)
        acquired_rules = manage_assignments.acquired_rules()
        assigned_rules = manage_assignments.assigned_rules()
        assignable_rules = manage_assignments.assignable_rules()

        return {
            "content-rules": {
                "acquired_rules": acquired_rules,
                "assigned_rules": assigned_rules,
                "assignable_rules": assignable_rules,
            }
        }
