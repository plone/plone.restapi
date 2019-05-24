# -*- coding: utf-8 -*-
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

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_roles_endpoint_lists_roles(self):
        response = self.api_session.get("/@roles")

        expected = (
            {
                u"@id": self.portal_url + u"/@roles/Contributor",
                u"@type": u"role",
                u"id": u"Contributor",
                u"title": u"Contributor",
            },
            {
                u"@id": self.portal_url + u"/@roles/Editor",
                u"@type": u"role",
                u"id": u"Editor",
                u"title": u"Editor",
            },
            {
                u"@id": self.portal_url + u"/@roles/Member",
                u"@type": u"role",
                u"id": u"Member",
                u"title": u"Member",
            },
            {
                u"@id": self.portal_url + u"/@roles/Reader",
                u"@type": u"role",
                u"id": u"Reader",
                u"title": u"Reader",
            },
            {
                u"@id": self.portal_url + u"/@roles/Reviewer",
                u"@type": u"role",
                u"id": u"Reviewer",
                u"title": u"Reviewer",
            },
            {
                u"@id": self.portal_url + u"/@roles/Site Administrator",
                u"@type": u"role",
                u"id": u"Site Administrator",
                u"title": u"Site Administrator",
            },
            {
                u"@id": self.portal_url + u"/@roles/Manager",
                u"@type": u"role",
                u"id": u"Manager",
                u"title": u"Manager",
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
        options = {u"Ver\xf6ffentlichen", u"Reviewer"}
        # One of the options must match:
        self.assertTrue(titles.intersection(options))
        # Discard them:
        titles = titles.difference(options)
        self.assertEqual(
            {
                u"Hinzuf\xfcgen",
                u"Bearbeiten",
                u"Benutzer",
                u"Ansehen",
                u"Website-Administrator",
                u"Verwalten",
            },
            titles,
        )
