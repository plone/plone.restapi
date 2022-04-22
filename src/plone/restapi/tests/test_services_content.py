"""
Test Rest API endpoints for retrieving content.
"""

from plone.restapi import testing

import transaction


class TestHistoryVersioning(testing.PloneRestAPIBrowserTestCase):
    """
    Test Rest API endpoints for retrieving content.
    """

    def setUp(self):
        """
        Create content to test against.
        """
        super().setUp()

        self.portal.invokeFactory(
            "Document", id="doc_with_history", title="My Document"
        )
        self.doc = self.portal.doc_with_history
        self.doc.setTitle("Current version")

        transaction.commit()

    def test_response(self):
        response = self.api_session.get(self.doc.absolute_url())
        self.assertIn("version", response.json())
