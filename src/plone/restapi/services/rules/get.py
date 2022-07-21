from zope.component import queryMultiAdapter
from plone.restapi.services import Service


class ContentRulesGet(Service):
    """Publishes the content rules assigned or acquired by given context"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@content-rules as parameters
        self.params.append(name)
        return self

    def reply(self):
        manage_assignments = queryMultiAdapter(
            (self.context, self.request), name="manage-content-rules"
        )
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
