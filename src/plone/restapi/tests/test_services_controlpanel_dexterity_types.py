# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
import unittest


class TestDexterityTypesControlpanel(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_controlpanels_dexterity_types_get(self):
        response = self.api_session.get("/@controlpanels/dexterity-types")
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [
                "Collection",
                "Document",
                "Folder",
                "Link",
                "File",
                "Image",
                "News Item",
                "Event",
                "DXTestDocument",
            ],
            [
                x.get("id")
                for x in self.api_session.get("/@controlpanels/dexterity-types")
                .json()
                .get("items")
            ],
        )

    def test_controlpanels_dexterity_types_document_get(self):
        response = self.api_session.get("/@controlpanels/dexterity-types/Document")
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            "{}/@controlpanels/dexterity-types/Document".format(self.portal_url),
            response.json().get("@id"),
        )
        self.assertEqual("Page", response.json().get("title"))

    def test_controlpanels_dexterity_types_post(self):
        response = self.api_session.post(
            "/@controlpanels/dexterity-types",
            json={
                "title": "My Custom Content Type",
                "description": "A custom content-type",
            },
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual(
            "{}/@controlpanels/dexterity-types/my_custom_content_type".format(
                self.portal_url
            ),
            response.json().get("@id"),
        )
        self.assertEqual("My Custom Content Type", response.json().get("title"))
        self.assertEqual("A custom content-type", response.json().get("description"))

    def test_controlpanels_dexterity_types_document_patch(self):
        response = self.api_session.patch(
            "/@controlpanels/dexterity-types/Document",
            json={
                "title": "New Content Type Title",
                "description": "New content type description",
            },
        )

        # PATCH returns no content
        self.assertEqual(204, response.status_code)

        response = self.api_session.get("/@controlpanels/dexterity-types/Document")
        self.assertEqual(200, response.status_code)
        self.assertEqual("New Content Type Title", response.json().get("title"))
        self.assertEqual(
            "New content type description", response.json().get("description")
        )

    def test_controlpanels_dexterity_types_document_delete(self):
        response = self.api_session.delete("/@controlpanels/dexterity-types/Document")

        self.assertEqual(204, response.status_code)
        self.assertEqual(
            [
                "Collection",
                "Folder",
                "Link",
                "File",
                "Image",
                "News Item",
                "Event",
                "DXTestDocument",
            ],
            [
                x.get("id")
                for x in self.api_session.get("/@controlpanels/dexterity-types")
                .json()
                .get("items")
            ],
        )
