"""Tests for Markdown renderer."""

from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.restapi.testing import PLONE_RESTAPI_BLOCKS_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

import requests
import transaction
import unittest


class TestMarkdownRendererClassic(unittest.TestCase):
    """Test the Markdown renderer with Accept: text/markdown header."""

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, SITE_OWNER_NAME)

        # Create a test document
        doc = api.content.create(
            container=self.portal,
            type="Document",
            id="test-doc",
            title="Test Document",
            description="A test document description",
            text=RichTextValue(
                "<p>This is <strong>bold</strong> and <em>italic</em> text.</p>",
                "text/html",
                "text/html",
            ),
        )
        self.doc = doc

        transaction.commit()

    def test_markdown_content_type_header(self):
        """Test that the content-type header is set correctly for Markdown."""
        response = requests.get(
            self.doc.absolute_url(),
            headers={"Accept": "text/markdown"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "text/markdown; charset=utf-8"
        )

    def test_markdown_basic_rendering(self):
        """Test that basic document is rendered as Markdown."""
        response = requests.get(
            self.doc.absolute_url(),
            headers={"Accept": "text/markdown"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        content = response.text

        # Check for YAML frontmatter
        self.assertIn("---", content)
        self.assertIn("'@id':", content)
        self.assertIn("'@type': Document", content)
        self.assertIn("title: Test Document", content)

        # Check for title as H1
        self.assertIn("# Test Document", content)

        # Check for converted HTML
        self.assertIn("**bold**", content)
        self.assertIn("*italic*", content)

    def test_json_still_works(self):
        """Test that JSON rendering still works with Accept: application/json."""
        response = requests.get(
            self.doc.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        data = response.json()
        self.assertEqual(data["@type"], "Document")
        self.assertEqual(data["title"], "Test Document")

    def test_default_to_json(self):
        """Test that without Accept header, it defaults to JSON."""
        url = self.doc.absolute_url().replace(
            self.portal_url, self.portal_url + "/++api++"
        )
        response = requests.get(
            url,
            headers={"Accept": "*/*"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")


class TestMarkdownRendererVolto(unittest.TestCase):
    """Test the Markdown renderer with Accept: text/markdown header."""

    layer = PLONE_RESTAPI_BLOCKS_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, SITE_OWNER_NAME)

        # Create a test document
        doc = api.content.create(
            container=self.portal,
            type="Document",
            id="test-doc",
            title="Test Document",
            description="A test document description",
            blocks={
                "block-id-1": {
                    "@type": "slate",
                    "plaintext": " This is bold text. ",
                    "value": [
                        {
                            "children": [
                                {"text": ""},
                                {
                                    "children": [{"text": "This is bold text."}],
                                    "type": "strong",
                                },
                                {"text": ""},
                            ],
                            "type": "p",
                        }
                    ],
                },
                "block-id-2": {
                    "@type": "slate",
                    "plaintext": " This is Italics. ",
                    "value": [
                        {
                            "children": [
                                {"text": ""},
                                {
                                    "children": [{"text": "This is Italics."}],
                                    "type": "em",
                                },
                                {"text": ""},
                            ],
                            "type": "p",
                        }
                    ],
                },
            },
            blocks_layout={"items": ["block-id-1", "block-id-2"]},
        )
        self.doc = doc

        transaction.commit()

    def test_markdown_content_type_header(self):
        """Test that the content-type header is set correctly for Markdown."""
        response = requests.get(
            self.doc.absolute_url(),
            headers={"Accept": "text/markdown"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "text/markdown; charset=utf-8"
        )

    def test_markdown_basic_rendering(self):
        """Test that basic document is rendered as Markdown."""
        response = requests.get(
            self.doc.absolute_url(),
            headers={"Accept": "text/markdown"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        content = response.text

        # Check for YAML frontmatter
        self.assertIn("---", content)
        self.assertIn("'@id':", content)
        self.assertIn("'@type': Document", content)
        self.assertIn("title: Test Document", content)

        # Check for title as H1
        self.assertIn("# Test Document", content)

        # Check for converted HTML
        self.assertIn("**This is bold text.**", content)
        self.assertIn("*This is Italics.*", content)

    def test_json_still_works(self):
        """Test that JSON rendering still works with Accept: application/json."""
        response = requests.get(
            self.doc.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        data = response.json()
        self.assertEqual(data["@type"], "Document")
        self.assertEqual(data["title"], "Test Document")

    def test_default_to_json(self):
        """Test that without Accept header, it defaults to JSON."""
        url = self.doc.absolute_url().replace(
            self.portal_url, self.portal_url + "/++api++"
        )
        response = requests.get(
            url,
            headers={"Accept": "*/*"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")
