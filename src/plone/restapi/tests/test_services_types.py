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

        self.api_session.post(
            "/@types/Document",
            json={
                "factory": "fieldset",
                "title": "Contact Info",
                "description": "Contact information",
            },
        )

        self.api_session.post(
            "/@types/Document",
            json={
                "factory": "fieldset",
                "title": "Location",
                "description": "Location",
            },
        )

        self.api_session.post(
            "/@types/Document",
            json={
                "factory": "Email",
                "title": "Author email",
                "description": "Email of the author",
            },
        )

        self.api_session.post(
            "/@types/Document",
            json={
                "factory": "URL",
                "title": "Author url",
                "description": "Website of the author",
            },
        )

    def tearDown(self):
        # Remove all custom changed on Document
        self.api_session.put("/@types/Document", json={})
        self.api_session.close()

    def test_get_types(self):
        response = self.api_session.get(f"{self.portal.absolute_url()}/@types")  # noqa

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
        response = self.api_session.get(f"{self.portal.absolute_url()}/@types/Document")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json+schema",
            "Sending a GET request to @types endpoint should respond with "
            + 'Content-Type: "application/json+schema", not '
            + '"{}"'.format(response.headers.get("Content-Type")),
        )

    def test_get_types_document_edit(self):
        response = self.api_session.get("/@types/Document")

        self.assertEqual(response.status_code, 200)

        # Fields are present
        self.assertIn("author_email", response.json().get("properties"))
        self.assertIn("author_url", response.json().get("properties"))

        # All fieldsets are present even empty ones
        self.assertIn(
            "location", [f["id"] for f in response.json().get("fieldsets")]
        )  # noqa
        self.assertIn(
            "contact_info", [f["id"] for f in response.json().get("fieldsets")]
        )  # noqa

    def test_types_document_get_fieldset(self):
        response = self.api_session.get("/@types/Document/contact_info")

        self.assertEqual(response.status_code, 200)
        self.assertEqual("Contact Info", response.json().get("title"))
        self.assertEqual(
            "Contact information", response.json().get("description")
        )  # noqa
        self.assertEqual("contact_info", response.json().get("id"))
        self.assertEqual([], response.json().get("fields"))

    def test_types_document_get_field(self):
        response = self.api_session.get("/@types/Document/author_email")

        self.assertEqual(response.status_code, 200)
        self.assertEqual("Author email", response.json().get("title"))  # noqa
        self.assertEqual(
            "Email of the author", response.json().get("description")
        )  # noqa
        self.assertTrue(
            response.json()
            .get("behavior")
            .startswith("plone.dexterity.schema.generated.plone_")
        )  # noqa
        self.assertEqual("string", response.json().get("type"))
        self.assertEqual("email", response.json().get("widget"))

    def test_types_document_post_fieldset(self):
        response = self.api_session.post(
            "/@types/Document",
            json={
                "factory": "fieldset",
                "title": "Foo bar",
                "description": "Foo bar tab",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual("Foo bar", response.json().get("title"))
        self.assertEqual("Foo bar tab", response.json().get("description"))  # noqa
        self.assertEqual("foo_bar", response.json().get("id"))
        self.assertEqual([], response.json().get("fields"))

    def test_types_document_post_field(self):
        response = self.api_session.post(
            "/@types/Document",
            json={
                "factory": "Email",
                "title": "Email",
                "description": "Foo bar email",
                "required": True,
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual("Email", response.json().get("title"))
        self.assertEqual("Foo bar email", response.json().get("description"))
        self.assertTrue(
            response.json()
            .get("behavior")
            .startswith("plone.dexterity.schema.generated.plone_")
        )  # noqa
        self.assertEqual("string", response.json().get("type"))
        self.assertEqual("email", response.json().get("widget"))

    def test_types_document_patch_properties(self):
        response = self.api_session.patch(
            "/@types/Document",
            json={
                "properties": {
                    "author_email": {
                        "default": "foo@bar.com",
                        "minLength": 5,
                        "maxLength": 100,
                    }
                }
            },
        )
        # PATCH returns no content
        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/@types/Document/author_email")
        self.assertEqual(200, response.status_code)
        self.assertEqual("foo@bar.com", response.json().get("default"))
        self.assertEqual(5, response.json().get("minLength"))
        self.assertEqual(100, response.json().get("maxLength"))

    def test_types_document_patch_fieldsets(self):
        response = self.api_session.patch(
            "/@types/Document",
            json={
                "fieldsets": [
                    {
                        "id": "contact_info",
                        "title": "Contact information",
                        "fields": ["author_email"],
                    }
                ]
            },
        )
        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/@types/Document/contact_info")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Contact information", response.json().get("title"))
        self.assertEqual(["author_email"], response.json().get("fields"))

    def test_types_document_patch_one_fieldset(self):
        response = self.api_session.patch(
            "/@types/Document/contact_info",
            json={
                "title": "Contact the author",
                "description": "Reach the author",
                "fields": [
                    "author_url",
                    "author_email",
                ],
            },
        )
        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/@types/Document/contact_info")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Contact the author", response.json().get("title"))
        self.assertEqual("Reach the author", response.json().get("description"))  # noqa
        self.assertEqual(
            ["author_url", "author_email"], response.json().get("fields")
        )  # noqa

    def test_types_document_patch_one_field(self):
        response = self.api_session.patch(
            "/@types/Document/author_email",
            json={
                "title": "Author e-mail",
                "description": "The e-mail address of the author",
                "minLength": 10,
                "maxLength": 200,
                "required": False,
            },
        )
        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/@types/Document/author_email")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Author e-mail", response.json().get("title"))
        self.assertEqual(
            "The e-mail address of the author", response.json().get("description")
        )  # noqa
        self.assertEqual(10, response.json().get("minLength"))
        self.assertEqual(200, response.json().get("maxLength"))

    def test_types_document_patch_create_missing(self):
        response = self.api_session.patch(
            "/@types/Document",
            json={
                "fieldsets": [
                    {"title": "Layout", "fields": ["blocks", "blocks_layout"]}
                ],
                "properties": {
                    "blocks": {
                        "title": "Blocks",
                        "type": "dict",
                        "widget": "json",
                        "factory": "JSONField",
                        "default": {
                            "230bdd04-6a0d-4cd2-ab60-4c09b315cc2c": {"@type": "title"},
                            "338013ce-acca-454f-a6f4-14113c187dca": {
                                "@type": "text",
                                "text": {
                                    "blocks": [
                                        {
                                            "data": {},
                                            "depth": 0,
                                            "entityRanges": [],
                                            "inlineStyleRanges": [],
                                            "key": "99pvk",
                                            "text": "Book summary",
                                            "type": "unstyled",
                                        }
                                    ],
                                    "entityMap": {},
                                },
                            },
                            "5060e030-727b-47bc-8023-b80b7cccd96f": {"@type": "image"},
                            "e3d8f8e4-8fee-47e7-9451-28724bf74a90": {"@type": "text"},
                        },
                    },
                    "blocks_layout": {
                        "title": "Blocks Layout",
                        "type": "dict",
                        "widget": "json",
                        "factory": "JSONField",
                        "default": {
                            "items": [
                                "230bdd04-6a0d-4cd2-ab60-4c09b315cc2c",
                                "338013ce-acca-454f-a6f4-14113c187dca",
                                "5060e030-727b-47bc-8023-b80b7cccd96f",
                                "e3d8f8e4-8fee-47e7-9451-28724bf74a90",
                            ]
                        },
                    },
                },
            },
        )
        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/@types/Document")
        self.assertEqual(200, response.status_code)

        self.assertIn("blocks", response.json().get("properties"))
        self.assertIn("blocks_layout", response.json().get("properties"))
        fieldsets = [
            f for f in response.json().get("fieldsets") if f.get("id") == "layout"
        ]  # noqa
        self.assertTrue(len(fieldsets) == 1)
        self.assertTrue(["blocks", "blocks_layout"], fieldsets[0].get("fields"))  # noqa

    def test_types_document_update_min_max(self):
        response = self.api_session.patch(
            "/@types/Document",
            json={
                "properties": {
                    "custom_text": {
                        "factory": "Text line (String)",
                        "minLength": 2,
                        "maxLength": 20,
                        "title": "Custom text",
                    },
                    "custom_float": {
                        "title": "Custom float",
                        "factory": "Floating-point number",
                        "minimum": 2.0,
                        "maximum": 14.0,
                    },
                }
            },
        )
        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/@types/Document/custom_text")
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.json().get("minLength"))
        self.assertEqual(20, response.json().get("maxLength"))

        response = self.api_session.get("/@types/Document/custom_float")
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, response.json().get("minimum"))
        self.assertEqual(14.0, response.json().get("maximum"))

    def test_types_document_put(self):
        response = self.api_session.get("/@types/Document")
        doc_json = response.json()
        doc_json["layouts"] = ["thumbnail_view", "table_view"]
        doc_json["fieldsets"] = [
            {
                "id": "author",
                "title": "Contact the author",
                "fields": ["author_email", "author_name"],
            },
            {"id": "contact_info", "title": "Contact info", "fields": []},
        ]

        doc_json["properties"]["author_name"] = {
            "description": "Name of the author",
            "factory": "Text line (String)",
            "title": "Author name",
        }
        doc_json["properties"].pop("author_url")

        doc_json["properties"]["author_email"] = {
            "minLength": 0,
            "maxLength": 100,
            "default": None,
        }

        response = self.api_session.put("/@types/Document", json=doc_json)
        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/@types/Document")
        self.assertEqual(200, response.status_code)

        # Layouts updated
        self.assertEqual(
            ["thumbnail_view", "table_view"], response.json().get("layouts")
        )  # noqa

        # Field added
        self.assertIn("author_name", response.json().get("properties"))

        # Field removed
        self.assertTrue("author_url" not in response.json().get("properties"))

        # Field updated
        self.assertEqual(
            None, response.json().get("properties").get("author_email").get("default")
        )  # noqa

        # Fieldset added
        self.assertIn(
            "author", [f["id"] for f in response.json().get("fieldsets")]
        )  # noqa

        # Fieldset removed
        self.assertTrue(
            "location" not in [f["id"] for f in response.json().get("fieldsets")]
        )  # noqa

        # Fieldset updated
        self.assertIn(
            "contact_info", [f["id"] for f in response.json().get("fieldsets")]
        )  # noqa

    def test_types_document_remove_field(self):
        response = self.api_session.delete(
            "/@types/Document/author_email",
        )
        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/@types/Document")
        self.assertEqual(200, response.status_code)

        self.assertTrue("author_email" not in response.json().get("properties"))  # noqa

    def test_types_document_remove_fieldset(self):
        response = self.api_session.delete(
            "/@types/Document/contact_info",
        )
        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/@types/Document")
        self.assertEqual(200, response.status_code)

        self.assertTrue(
            "contact_info" not in [f["id"] for f in response.json().get("fieldsets")]
        )  # noqa

    def test_get_types_with_unknown_type(self):
        response = self.api_session.get(
            f"{self.portal.absolute_url()}/@types/UnknownType"
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
        response = self.api_session.get(f"{self.portal.absolute_url()}/@types")  # noqa
        self.assertEqual(response.status_code, 401)

    def test_contextaware_addable(self):
        response = self.api_session.get(f"{self.portal.absolute_url()}/@types")  # noqa

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
        self.assertIn(
            "image.data", response["properties"]["image"]["properties"]
        )  # noqa

    def test_file_type(self):
        response = self.api_session.get("/@types/File")
        response = response.json()
        self.assertIn("fieldsets", response)
        self.assertIn("file.data", response["properties"]["file"]["properties"])  # noqa

    def test_event_type(self):
        response = self.api_session.get("/@types/Event")
        response = response.json()
        self.assertIn("title", response["properties"]["start"])

    def test_addable_types_for_non_manager_user(self):
        user = api.user.create(
            email="noam.chomsky@example.com", username="noam", password="12345"
        )

        folder = api.content.create(
            container=self.portal, id="folder", type="Folder", title="folder"
        )

        folder_cant_add = api.content.create(
            container=self.portal,
            id="folder_cant_add",
            type="Folder",
            title="folder_cant_add",
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
        response = self.api_session.get(f"{self.portal.absolute_url()}/@types")  # noqa

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            {
                "Archivo",
                "Carpeta",
                "Colección",
                "DX Test Document",
                "Enlace",
                "Evento",
                "Imagen",
                "Noticia",
                "Página",
            },
            {item["title"] for item in response.json()},
        )
