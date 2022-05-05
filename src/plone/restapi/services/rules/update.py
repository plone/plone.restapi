from plone.app.contentrules.browser.assignments import ManageAssignments
from plone.restapi.services import Service
import plone.protect.interfaces
from zope.interface import alsoProvides
from plone.restapi.deserializer import json_body


class RulesUpdate(Service):
    """Update rules"""

    def reply(self):

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        data = json_body(self.request)
        operation = data.get('operation', None)
        if operation:
            self.request.form['operation'] = operation
        rule_id = data.get('rule_id', None)
        if rule_id:
            self.request.form['rule_id'] = rule_id
        rule_ids = data.get('rule_ids', None)
        if rule_ids:
            self.request.form['rule_ids'] = rule_ids
        enable = data.get('form.button.Enable', None)
        if 'form.button.Enable':
            self.request.form['form.button.Enable'] = enable
        disable = data.get('form.button.Disable', None)
        if disable:
            self.request.form['form.button.Disable'] = disable
        bubble = data.get('form.button.Bubble', None)
        if bubble:
            self.request.form['form.button.Bubble'] = bubble
        no_bubble = data.get('form.button.NoBubble', None)
        if no_bubble:
            self.request.form['form.button.NoBubble'] = no_bubble

        ManageAssignments(self.context, self.request)()
        return self.reply_no_content()
