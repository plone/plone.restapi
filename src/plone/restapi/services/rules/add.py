from plone.restapi.services import Service
import plone.protect.interfaces
from zExceptions import BadRequest
from zope.interface import implementer
from zope.interface import alsoProvides
from zope.component import queryMultiAdapter
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class ContentRulesAdd(Service):
    """Adds content rules"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@content-rules as parameters
        self.params.append(name)
        return self

    def reply(self):

        if not self.params:
            raise BadRequest("Missing parameter rule_id")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        rule_id = self.params[0]
        self.request.form["form.button.AddAssignment"] = True
        self.request.form["rule_id"] = rule_id
        manage_assignments = queryMultiAdapter(
            (self.context, self.request), name="manage-content-rules"
        )
        manage_assignments()
        return {"message": "Successfully assigned the rule %s" % rule_id}
