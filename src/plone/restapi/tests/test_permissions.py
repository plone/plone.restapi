"""
Test Rest API handling of authenticated user permissions.
"""

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.permissions import UseRESTAPI
from plone.restapi import testing

import transaction


class TestPermissions(testing.PloneRestAPIBrowserTestCase):
    """
    Test Rest API handling of authenticated user permissions.
    """

    def setUp(self):
        """
        Log the browser session in as the normal test user.
        """
        super().setUp()

        self.api_session.auth = (TEST_USER_NAME, TEST_USER_PASSWORD)

    def test_anonymous_allowed_to_use_api_by_default(self):
        setRoles(self.portal, TEST_USER_ID, ["Anonymous"])
        transaction.commit()

        response = self.api_session.get(self.portal_url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_allowed_to_use_api_by_default(self):
        setRoles(self.portal, TEST_USER_ID, ["Authenticated"])
        transaction.commit()

        response = self.api_session.get(self.portal_url)
        self.assertEqual(response.status_code, 200)

    def test_manager_allowed_to_use_api_by_default(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        transaction.commit()

        response = self.api_session.get(self.portal_url)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_if_missing_permission(self):
        # Unmap the 'plone.restapi: Use REST API'
        # permission from any roles
        self.portal.manage_permission(UseRESTAPI, roles=[])
        transaction.commit()

        response = self.api_session.get(self.portal_url)
        self.assertEqual(response.status_code, 401)
        self.assertDictContainsSubset(
            {
                "type": "Unauthorized",
                "message": "Missing 'plone.restapi: Use REST API' permission",
            },
            response.json(),
        )
