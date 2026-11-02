from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import logging
import plone.protect

logger = logging.getLogger(__name__)

# Contact forms hide this field with CSS, so only bots fill it in.
HONEYPOT_FIELD = "website"


class EmailNotificationPost(Service):
    def reply(self):
        data = json_body(self.request)

        if data.get(HONEYPOT_FIELD):
            # Answer as if the email was sent, so the bot does not try again.
            # Log it to count them, but not the value or the message: a browser
            # may have filled it in after all.
            logger.info("Spam blocked: reason=honeypot form=@email-notification")
            return self.reply_no_content()

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
