from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import unittest


class TestRolesGet(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

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
