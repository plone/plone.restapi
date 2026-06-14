from email import message_from_string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.MailHost.interfaces import IMailHost
from zope.component import getUtility

import transaction
import unittest


class EmailSendEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.mailhost = getUtility(IMailHost)

        registry = getUtility(IRegistry)
        registry["plone.email_from_address"] = "info@plone.org"
        registry["plone.email_from_name"] = "Plone test site"

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        self.anon_api_session = RelativeSession(self.portal_url, test=self)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        transaction.commit()

    def tearDown(self):
        self.api_session.close()
        self.anon_api_session.close()

    def test_email_send(self):
        response = self.api_session.post(
            "/@email-send",
            json={
                "to": "jane@doe.com",
                "from": "john@doe.com",
                "message": "Just want to say hi.",
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            # Python 3 with Products.MailHost 4.10+
            msg = msg.decode("utf-8")
        self.assertTrue("Subject: =?utf-8?q?A_portal_user_via_Plone_site?=" in msg)
        self.assertTrue("From: info@plone.org" in msg)
        self.assertTrue("Reply-To: john@doe.com" in msg)
        self.assertTrue("Just want to say hi." in msg)

    def test_email_send_all_parameters(self):
        response = self.api_session.post(
            "/@email-send",
            json={
                "to": "jane@doe.com",
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
        self.assertTrue("From: info@plone.org" in msg)
        self.assertTrue("John Doe" in msg)
        self.assertTrue("Reply-To: john@doe.com" in msg)
        self.assertTrue("Just want to say hi." in msg)

    def test_email_send_anonymous(self):
        response = self.anon_api_session.post(
            "/@email-send",
            json={
                "to": "jane@doe.com",
                "from": "john@doe.com",
                "message": "Just want to say hi.",
                "name": "John Doe",
                "subject": "This is the subject.",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_email_send_plain_text_has_intro(self):
        response = self.api_session.post(
            "/@email-send",
            json={
                "to": "jane@doe.com",
                "from": "john@doe.com",
                "message": "This is a plain text message.",
                "name": "John Doe",
                "subject": "Test Subject",
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            msg = msg.decode("utf-8")

        self.assertTrue("You are receiving this mail because" in msg)
        self.assertTrue("John Doe" in msg)
        self.assertTrue("This is a plain text message." in msg)
        intro_pos = msg.find("You are receiving this mail because")
        message_pos = msg.find("This is a plain text message.")
        self.assertGreater(
            message_pos, intro_pos, "Intro text should appear before message"
        )

    def test_email_send_multipart_no_intro(self):
        multipart_msg = MIMEMultipart("alternative")
        multipart_msg["Subject"] = "Test Multipart"
        multipart_msg["From"] = "sender@example.com"
        multipart_msg["To"] = "recipient@example.com"

        text_part = MIMEText("This is the plain text version.", "plain")
        html_part = MIMEText(
            "<html><body>This is the <b>HTML</b> version.</body></html>", "html"
        )

        multipart_msg.attach(text_part)
        multipart_msg.attach(html_part)

        message_str = multipart_msg.as_string()

        response = self.api_session.post(
            "/@email-send",
            json={
                "to": "jane@doe.com",
                "from": "john@doe.com",
                "message": message_str,
                "name": "John Doe",
                "subject": "Test Multipart Subject",
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            msg = msg.decode("utf-8")

        self.assertFalse("You are receiving this mail because" in msg)
        self.assertTrue("multipart/alternative" in msg)
        self.assertTrue("This is the plain text version." in msg)
        self.assertTrue("This is the <b>HTML</b> version." in msg)

    def test_email_send_multipart_structure_preserved(self):
        multipart_msg = MIMEMultipart("alternative")
        text_part = MIMEText("Plain text content here.", "plain")
        html_part = MIMEText(
            "<html><body><p>HTML content here.</p></body></html>", "html"
        )

        multipart_msg.attach(text_part)
        multipart_msg.attach(html_part)

        message_str = multipart_msg.as_string()

        response = self.api_session.post(
            "/@email-send",
            json={
                "to": "jane@doe.com",
                "from": "john@doe.com",
                "message": message_str,
                "subject": "Structure Test",
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            msg = msg.decode("utf-8")

        parsed_msg = message_from_string(msg)

        self.assertTrue(parsed_msg.is_multipart())
        self.assertTrue("multipart/alternative" in parsed_msg.get_content_type())
        parts = list(parsed_msg.walk())
        self.assertEqual(len(parts), 3)
        text_found = False
        html_found = False
        for part in parts:
            if part.get_content_type() == "text/plain":
                self.assertTrue("Plain text content here." in part.get_payload())
                text_found = True
            elif part.get_content_type() == "text/html":
                self.assertTrue("HTML content here." in part.get_payload())
                html_found = True
        self.assertTrue(text_found, "Text part not found")
        self.assertTrue(html_found, "HTML part not found")

    def test_email_send_multipart_with_attachment(self):
        """Test that multipart messages with attachments are handled correctly."""
        from email import encoders
        from email.mime.base import MIMEBase

        multipart_msg = MIMEMultipart()
        multipart_msg["Subject"] = "Test with Attachment"
        multipart_msg["From"] = "sender@example.com"
        multipart_msg["To"] = "recipient@example.com"

        text_part = MIMEText("This message has an attachment.", "plain")
        multipart_msg.attach(text_part)

        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(b"Test attachment content")
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            'attachment; filename="test.txt"',
        )
        multipart_msg.attach(attachment)

        message_str = multipart_msg.as_string()

        response = self.api_session.post(
            "/@email-send",
            json={
                "to": "jane@doe.com",
                "from": "john@doe.com",
                "message": message_str,
                "subject": "Attachment Test",
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        msg = self.mailhost.messages[0]
        if isinstance(msg, bytes) and bytes is not str:
            msg = msg.decode("utf-8")

        self.assertFalse("You are receiving this mail because" in msg)
        self.assertTrue("multipart" in msg.lower())
        self.assertTrue("Content-Disposition" in msg)
        self.assertTrue("attachment" in msg.lower())
