from plone import api
from plone.base import PloneMessageFactory as _
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.statusmessages.interfaces import IStatusMessage
from smtplib import SMTPException
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import logging
import plone.protect

try:
    # Products.MailHost has a patch to fix quoted-printable soft line breaks.
    # See https://github.com/zopefoundation/Products.MailHost/issues/35
    from Products.MailHost.MailHost import message_from_string
except ImportError:
    # If the patch is ever removed, we fall back to the standard library.
    from email import message_from_string

logger = logging.getLogger(__name__)


class EmailNotificationPost(Service):
    """Send email notifications."""

    def generate_mail(self, variables, template):
        result = template(self.context, **variables)
        return result

    def reply(self):
        data = json_body(self.request)

        from_address = data.get("from", None)
        message = data.get("message", None)
        sender_fullname = data.get("name", "")
        subject = data.get("subject", "")
        template = data.get("template", "contact-info")

        if not from_address or not message:
            raise BadRequest("Missing from or message parameters")

        overview_controlpanel = getMultiAdapter(
            (self.context, self.request), name="overview-controlpanel"
        )
        if not from_address and overview_controlpanel.mailhost_warning():
            raise BadRequest("MailHost is not configured.")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        if template:
            template = getMultiAdapter((self.context, self.request), name=template)
            message = self.generate_mail(data, template)

        host = api.portal.get_tool("MailHost")

        data["url"] = api.portal.get().absolute_url()
        message = message_from_string(message)
        message["Reply-To"] = from_address
        to_address = from_address

        try:
            # This actually sends out the mail
            host.send(
                message,
                to_address,
                from_address,
                subject=subject,
            )
        except (SMTPException, RuntimeError) as e:
            logger.error(e)
            plone_utils = api.portal.get_tool("plone_utils")
            exception = plone_utils.exceptionString()
            message = _(
                "Unable to send mail: ${exception}", mapping={"exception": exception}
            )
            IStatusMessage(self.request).add(message, type="error")

        return self.reply_no_content()
