# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestServicesTypes(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_get_types(self):
        response = self.api_session.get("{}/@types".format(self.portal.absolute_url()))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json",
            "Sending a GET request to @types endpoint should respond with "
            + 'Content-Type: "application/json", not '
            + '"{}"'.format(response.headers.get("Content-Type")),
        )
        for item in response.json():
            self.assertEqual(sorted(item), sorted(["@id", "title", "addable"]))

    def test_get_types_document(self):
        response = self.api_session.get(
            "{}/@types/Document".format(self.portal.absolute_url())
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json+schema",
            "Sending a GET request to @types endpoint should respond with "
            + 'Content-Type: "application/json+schema", not '
            + '"{}"'.format(response.headers.get("Content-Type")),
        )

    def test_get_types_with_unknown_type(self):
        response = self.api_session.get(
            "{}/@types/UnknownType".format(self.portal.absolute_url())
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            "application/json",
            response.headers.get("Content-Type"),
            "Sending a GET request to @types endpoint should respond with "
            + 'Content-Type: "application/json", not '
            + '"{}"'.format(response.headers.get("Content-Type")),
        )

    def test_types_endpoint_only_accessible_for_authenticated_users(self):
        self.api_session.auth = ()
        response = self.api_session.get("{}/@types".format(self.portal.absolute_url()))
        self.assertEqual(response.status_code, 401)

    def test_contextaware_addable(self):
        response = self.api_session.get("{}/@types".format(self.portal.absolute_url()))

        allowed_ids = [x.getId() for x in self.portal.allowedContentTypes()]

        response_allowed_ids = [
            x["@id"].split("/")[-1] for x in response.json() if x["addable"]
        ]

        # We check subset here, because only DX types are returned by the
        # endpoint.
        self.assertNotEqual([], allowed_ids)
        self.assertTrue(set(response_allowed_ids).issubset(set(allowed_ids)))

    def test_image_type(self):
        response = self.api_session.get("/@types/Image")
        response = response.json()
        self.assertIn("fieldsets", response)
        self.assertIn("image.data", response["properties"]["image"]["properties"])

    def test_file_type(self):
        response = self.api_session.get("/@types/File")
        response = response.json()
        self.assertIn("fieldsets", response)
        self.assertIn("file.data", response["properties"]["file"]["properties"])

    def test_event_type(self):
        response = self.api_session.get("/@types/Event")
        response = response.json()
        self.assertIn("title", response["properties"]["start"])

    def test_addable_types_for_non_manager_user(self):
        user = api.user.create(
            email="noam.chomsky@example.com", username="noam", password="12345"
        )

        folder = api.content.create(
            container=self.portal, id="folder", type="Folder", title=u"folder"
        )

        folder_cant_add = api.content.create(
            container=self.portal,
            id="folder_cant_add",
            type="Folder",
            title=u"folder_cant_add",
        )

        api.user.grant_roles(user=user, obj=folder, roles=["Contributor"])

        api.user.grant_roles(user=user, obj=folder_cant_add, roles=["Reader"])

        transaction.commit()

        self.api_session.auth = ("noam", "12345")
        # In the folder, the user should be able to add types since we granted
        # Contributor role on it
        response = self.api_session.get("/folder/@types")
        response = response.json()

        # Any addable type will do.
        self.assertTrue(any(a["addable"] for a in response))

        # In the folder where the user only have Reader role, no types are
        # addable
        response = self.api_session.get("/folder_cant_add/@types")
        response = response.json()

        self.assertEqual(len([a for a in response if a["addable"]]), 0)

        # and in the root Plone site there's no addable types
        response = self.api_session.get("/@types")
        response = response.json()

        self.assertEqual(len([a for a in response if a["addable"]]), 0)


class TestServicesTypesTranslatedTitles(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.headers.update({"Accept-Language": "es"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_get_types_translated(self):
        response = self.api_session.get("{}/@types".format(self.portal.absolute_url()))

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            {
                u"Archivo",
                u"Carpeta",
                u"Colección",
                u"DX Test Document",
                u"Enlace",
                u"Evento",
                u"Imagen",
                u"Noticia",
                u"Página",
            },
            set(item["title"] for item in response.json()),
        )
