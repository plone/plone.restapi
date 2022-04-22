"""
Test Rest API support for retrieving available local roles.
"""

from plone.restapi import testing


class TestRolesGet(testing.PloneRestAPIBrowserTestCase):
    """
    Test Rest API support for retrieving available local roles.
    """

    def test_roles_endpoint_lists_roles(self):
        response = self.api_session.get("/@roles")

        expected = (
            {
                "@id": self.portal_url + "/@roles/Contributor",
                "@type": "role",
                "id": "Contributor",
                "title": "Contributor",
            },
            {
                "@id": self.portal_url + "/@roles/Editor",
                "@type": "role",
                "id": "Editor",
                "title": "Editor",
            },
            {
                "@id": self.portal_url + "/@roles/Member",
                "@type": "role",
                "id": "Member",
                "title": "Member",
            },
            {
                "@id": self.portal_url + "/@roles/Reader",
                "@type": "role",
                "id": "Reader",
                "title": "Reader",
            },
            {
                "@id": self.portal_url + "/@roles/Reviewer",
                "@type": "role",
                "id": "Reviewer",
                "title": "Reviewer",
            },
            {
                "@id": self.portal_url + "/@roles/Site Administrator",
                "@type": "role",
                "id": "Site Administrator",
                "title": "Site Administrator",
            },
            {
                "@id": self.portal_url + "/@roles/Manager",
                "@type": "role",
                "id": "Manager",
                "title": "Manager",
            },
        )
        result = response.json()
        self.assertEqual(len(expected), len(result))
        for item in result:
            self.assertIn(item, expected)

    def test_roles_endpoint_translates_role_titles(self):
        self.api_session.headers.update({"Accept-Language": "de"})
        response = self.api_session.get("/@roles")
        # One of the roles has changed translation in German.
        # Reviewer used to be 'Ver\xf6ffentlichen', but is now simply Reviewer.
        titles = {item["title"] for item in response.json()}
        options = {"Ver\xf6ffentlichen", "Reviewer"}
        # One of the options must match:
        self.assertTrue(titles.intersection(options))
        # Discard them:
        titles = titles.difference(options)
        self.assertEqual(
            {
                "Hinzuf\xfcgen",
                "Bearbeiten",
                "Benutzer",
                "Ansehen",
                "Website-Administrator",
                "Verwalten",
            },
            titles,
        )
