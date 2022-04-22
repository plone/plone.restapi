"""
Test Rest API endpoints for retrieving principals data.
"""

from plone import api
from plone.restapi import testing

import transaction


class TestPrincipalsEndpoint(testing.PloneRestAPIBrowserTestCase):
    """
    Test Rest API endpoints for retrieving principals data.
    """

    def setUp(self):
        """
        Create a user and group to test against.
        """
        super().setUp()

        properties = {
            "email": "noam.chomsky@example.com",
            "username": "noamchomsky",
            "fullname": "Noam Avram Chomsky",
            "home_page": "web.mit.edu/chomsky",
            "description": "Professor of Linguistics",
            "location": "Cambridge, MA",
        }
        self.user = api.user.create(
            email="noam.chomsky@example.com", username="noam", properties=properties
        )

        self.gtool = api.portal.get_tool("portal_groups")
        properties = {
            "title": "Plone Team",
            "description": "We are Plone",
            "email": "ploneteam@plone.org",
        }
        self.gtool.addGroup(
            "ploneteam",
            (),
            (),
            properties=properties,
            title=properties["title"],
            description=properties["description"],
        )
        transaction.commit()

    def test_get_principals(self):
        response = self.api_session.get("/@principals", params={"search": "noam"})
        self.assertEqual(200, response.status_code)

        response = response.json()
        self.assertEqual(2, len(response))
        self.assertEqual(1, len(response["users"]))
        self.assertEqual("noam", response["users"][0]["id"])

        response = self.api_session.get("/@principals", params={"search": "plone"})
        self.assertEqual(200, response.status_code)

        response = response.json()
        self.assertEqual(2, len(response))
        self.assertEqual(1, len(response["groups"]))
        self.assertEqual("ploneteam", response["groups"][0]["id"])

    def test_get_principals_response_both(self):
        self.user = api.user.create(
            email="plone.user@example.com", username="plone.user"
        )
        transaction.commit()

        response = self.api_session.get("/@principals", params={"search": "plone"})
        self.assertEqual(200, response.status_code)

        response = response.json()
        self.assertEqual(2, len(response))
        self.assertEqual(1, len(response["users"]))
        self.assertEqual(1, len(response["groups"]))
        self.assertEqual("plone.user", response["users"][0]["id"])
        self.assertEqual("ploneteam", response["groups"][0]["id"])
