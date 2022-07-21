from plone.restapi.services import Service
import plone.protect.interfaces
from zope.interface import alsoProvides
from zope.component import queryMultiAdapter
from plone.restapi.deserializer import json_body


class ContentRulesUpdate(Service):
    """Update content rules"""

    def reply(self):

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        data = json_body(self.request)
        operation = data.get("operation", None)
        if operation:
            self.request.form["operation"] = operation
            message = "Successfully applied the %s" % operation
        rule_id = data.get("rule_id", None)
        if rule_id:
            self.request.form["rule_id"] = rule_id
        rule_ids = data.get("rule_ids", None)
        if rule_ids:
            self.request.form["rule_ids"] = rule_ids
        enable = data.get("form.button.Enable", None)
        if enable:
            self.request.form["form.button.Enable"] = enable
            message = "Successfully enabled rules %s" % rule_ids
        disable = data.get("form.button.Disable", None)
        if disable:
            self.request.form["form.button.Disable"] = disable
            message = "Successfully disabled rules %s" % rule_ids
        bubble = data.get("form.button.Bubble", None)
        if bubble:
            self.request.form["form.button.Bubble"] = bubble
            message = "Successfully applied %s to subfolders" % rule_ids
        no_bubble = data.get("form.button.NoBubble", None)
        if no_bubble:
            self.request.form["form.button.NoBubble"] = no_bubble
            message = "Disabled apply to subfolders for %s" % rule_ids

        manage_assignments = queryMultiAdapter(
            (self.context, self.request), name="manage-content-rules"
        )
        manage_assignments()
        return {"message": message}
