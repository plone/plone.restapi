from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import plone


class EmailNotificationPost(Service):
    def reply(self):
        data = json_body(self.request)

        sender_from_address = data.get("from", None)
        message = data.get("message", None)
        sender_fullname = data.get("name", "")
        subject = data.get("subject", "")

        if not sender_from_address or not message:
            raise BadRequest("Missing from or message parameters")

        overview_controlpanel = getMultiAdapter(
            (self.context, self.request), name="overview-controlpanel"
        )
        if overview_controlpanel.mailhost_warning():
            raise BadRequest("MailHost is not configured.")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        contact_info_view = getMultiAdapter(
            (self.context, self.request), name="contact-info"
        )

        contact_info_view.send_message(
            dict(
                message=message,
                subject=subject,
                sender_from_address=sender_from_address,
                sender_fullname=sender_fullname,
            )
        )

        return self.reply_no_content()
