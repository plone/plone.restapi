from plone.restapi.services import Service
import plone.protect.interfaces
from zExceptions import BadRequest
from zope.interface import alsoProvides
from zope.component import queryMultiAdapter
from plone.restapi.deserializer import json_body


class ContentRulesDelete(Service):
    """Delete content rules"""

    def reply(self):

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        data = json_body(self.request)
        rule_ids = data.get("rule_ids")
        if not rule_ids:
            raise BadRequest("Missing parameter rule_ids")

        self.request.form["form.button.Delete"] = True
        self.request.form["rule_ids"] = rule_ids
        manage_assignments = queryMultiAdapter(
            (self.context, self.request), name="manage-content-rules"
        )
        manage_assignments()
        return self.reply_no_content()
