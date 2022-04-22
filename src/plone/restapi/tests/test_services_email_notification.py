"""
Test Rest API endpoints for sending email notifications.
"""

from plone.registry.interfaces import IRegistry
from plone.restapi import testing
from plone.restapi.testing import RelativeSession
from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility

import transaction


class EmailNotificationEndpoint(testing.PloneRestAPIBrowserTestCase):
    """
    Test Rest API endpoints for sending email notifications.
    """

    def setUp(self):
        """
        Set registry records needed to test sending mail.
        """
        super().setUp()

        self.mailhost = getUtility(IMailHost)

        registry = getUtility(IRegistry)
        registry["plone.email_from_address"] = "info@plone.org"
        registry["plone.email_from_name"] = "Plone test site"

        self.anon_api_session = RelativeSession(self.portal_url, test=self)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        transaction.commit()

    def test_email_notification_missing_parameters(self):
        response = self.api_session.post(
            "/@email-notification", json={"message": "Just want to say hi."}
        )
        transaction.commit()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.mailhost.messages, [])
        error = response.json()
        self.assertEqual(error["message"], "Missing from or message parameters")

    def test_email_notification(self):
        response = self.api_session.post(
            "/@email-notification",
            json={"from": "john@doe.com", "message": "Just want to say hi."},
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            # Python 3 with Products.MailHost 4.10+
            msg = msg.decode("utf-8")
        self.assertTrue("Subject: [No Subject]" in msg)
        self.assertTrue("To: info@plone.org" in msg)
        self.assertTrue("Reply-To: john@doe.com" in msg)
        self.assertTrue("Just want to say hi." in msg)

    def test_email_notification_all_parameters(self):
        response = self.api_session.post(
            "/@email-notification",
            json={
                "from": "john@doe.com",
                "message": "Just want to say hi.",
                "name": "John Doe",
                "subject": "This is the subject.",
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            # Python 3 with Products.MailHost 4.10+
            msg = msg.decode("utf-8")
        self.assertTrue("=?utf-8?q?This_is_the_subject" in msg)
        self.assertTrue("To: info@plone.org" in msg)
        self.assertTrue("John Doe" in msg)
        self.assertTrue("Reply-To: john@doe.com" in msg)
        self.assertTrue("Just want to say hi." in msg)
