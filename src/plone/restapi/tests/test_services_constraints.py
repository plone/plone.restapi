from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.bbb import ISelectableConstrainTypes
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestServicesConstraints(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Folder", id="folder", title="My Folder")
        self.portal.invokeFactory("Document", id="doc", title="My Document")
        transaction.commit()

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_get_folder_constraints(self):
        response = self.api_session.get("/folder/@constraints")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["configurable"])
        self.assertTrue(data["can_edit"])
        self.assertEqual(data["mode"], "disabled")
        self.assertIn("Document", data["locally_allowed_types"])
        self.assertIn("Document", data["immediately_addable_types"])
        addable_ids = {item["id"] for item in data["addable_types"]}
        self.assertIn("Document", addable_ids)
        self.assertTrue(all("title" in item for item in data["addable_types"]))
        self.assertEqual(data["@id"], f"{self.portal_url}/folder/@constraints")

    def test_get_site_root_constraints(self):
        # Endpoint must be registered on the site root even when the Plone
        # Site itself is not ISelectableConstrainTypes-adaptable.
        response = self.api_session.get("/@constraints")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("configurable", data)
        self.assertIn("can_edit", data)
        self.assertIn("addable_types", data)

    def test_get_document_is_not_configurable(self):
        response = self.api_session.get("/doc/@constraints")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["configurable"])
        self.assertFalse(data["can_edit"])
        self.assertIsNone(data["mode"])
        self.assertEqual(data["addable_types"], [])
        self.assertEqual(data["locally_allowed_types"], [])
        self.assertEqual(data["immediately_addable_types"], [])

    def test_get_addable_types_not_filtered_by_constraints(self):
        self.api_session.patch(
            "/folder/@constraints",
            json={
                "mode": "enabled",
                "locally_allowed_types": ["Document"],
                "immediately_addable_types": ["Document"],
            },
        )
        response = self.api_session.get("/folder/@constraints")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["locally_allowed_types"], ["Document"])
        addable_ids = {item["id"] for item in data["addable_types"]}
        self.assertIn("Document", addable_ids)
        self.assertIn("News Item", addable_ids)

    def test_patch_enabled_constraints(self):
        response = self.api_session.patch(
            "/folder/@constraints",
            headers={"Prefer": "return=representation"},
            json={
                "mode": "enabled",
                "locally_allowed_types": ["Document", "News Item"],
                "immediately_addable_types": ["News Item"],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["mode"], "enabled")
        self.assertEqual(data["locally_allowed_types"], ["Document", "News Item"])
        self.assertEqual(data["immediately_addable_types"], ["News Item"])

        transaction.commit()
        adapter = ISelectableConstrainTypes(self.portal.folder)
        self.assertEqual(adapter.getConstrainTypesMode(), 1)
        self.assertEqual(
            set(adapter.getLocallyAllowedTypes()), {"Document", "News Item"}
        )
        self.assertEqual(set(adapter.getImmediatelyAddableTypes()), {"News Item"})

    def test_patch_returns_no_content_by_default(self):
        response = self.api_session.patch(
            "/folder/@constraints",
            json={
                "mode": "enabled",
                "locally_allowed_types": ["Document"],
                "immediately_addable_types": ["Document"],
            },
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(response.content)

    def test_patch_updates_effective_types(self):
        response = self.api_session.patch(
            "/folder/@constraints",
            json={
                "mode": "enabled",
                "locally_allowed_types": ["Image", "File"],
                "immediately_addable_types": ["Image"],
            },
        )
        self.assertEqual(response.status_code, 204)
        transaction.commit()

        types = self.api_session.get("/folder/@types").json()
        addable = {item["id"] for item in types if item["addable"]}
        immediately = {item["id"] for item in types if item["immediately_addable"]}
        self.assertEqual(addable, {"Image", "File"})
        self.assertEqual(immediately, {"Image"})

    def test_patch_partial_locally_allowed_intersects_immediately(self):
        self.api_session.patch(
            "/folder/@constraints",
            json={
                "mode": "enabled",
                "locally_allowed_types": ["Document", "News Item"],
                "immediately_addable_types": ["Document", "News Item"],
            },
        )
        response = self.api_session.patch(
            "/folder/@constraints",
            headers={"Prefer": "return=representation"},
            json={"locally_allowed_types": ["Document"]},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["locally_allowed_types"], ["Document"])
        self.assertEqual(data["immediately_addable_types"], ["Document"])

        transaction.commit()
        types = self.api_session.get("/folder/@types").json()
        news_item = next(item for item in types if item["id"] == "News Item")
        self.assertFalse(news_item["addable"])
        self.assertFalse(news_item["immediately_addable"])

    def test_patch_acquire_mode(self):
        self.portal.folder.invokeFactory("Folder", id="child", title="Child")
        transaction.commit()
        response = self.api_session.patch(
            "/folder/child/@constraints",
            headers={"Prefer": "return=representation"},
            json={"mode": "acquire"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mode"], "acquire")

    def test_patch_invalid_mode(self):
        response = self.api_session.patch(
            "/folder/@constraints",
            json={"mode": "manual"},
        )
        self.assertEqual(response.status_code, 400)

    def test_patch_invalid_type(self):
        response = self.api_session.patch(
            "/folder/@constraints",
            json={
                "mode": "enabled",
                "locally_allowed_types": ["NotAType"],
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_patch_immediately_must_be_subset(self):
        response = self.api_session.patch(
            "/folder/@constraints",
            json={
                "mode": "enabled",
                "locally_allowed_types": ["Document"],
                "immediately_addable_types": ["News Item"],
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_patch_document_is_rejected(self):
        response = self.api_session.patch(
            "/doc/@constraints",
            json={"mode": "enabled"},
        )
        self.assertEqual(response.status_code, 400)

    def test_get_requires_add_permission(self):
        api.user.create(
            email="viewer@example.com",
            username="viewer",
            password="password",
        )
        transaction.commit()
        session = RelativeSession(self.portal_url, test=self)
        session.headers.update({"Accept": "application/json"})
        session.auth = ("viewer", "password")
        try:
            response = session.get("/folder/@constraints")
            self.assertIn(response.status_code, (401, 403))
        finally:
            session.close()

    def test_get_allowed_for_contributor(self):
        api.user.create(
            email="contributor@example.com",
            username="contributor",
            password="password",
        )
        api.user.grant_roles(username="contributor", roles=["Contributor"])
        transaction.commit()
        session = RelativeSession(self.portal_url, test=self)
        session.headers.update({"Accept": "application/json"})
        session.auth = ("contributor", "password")
        try:
            response = session.get("/folder/@constraints")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["configurable"])
            self.assertFalse(data["can_edit"])
        finally:
            session.close()

    def test_patch_requires_modify_constrain_types(self):
        api.user.create(
            email="contributor@example.com",
            username="contributor",
            password="password",
        )
        api.user.grant_roles(username="contributor", roles=["Contributor"])
        transaction.commit()
        session = RelativeSession(self.portal_url, test=self)
        session.headers.update({"Accept": "application/json"})
        session.auth = ("contributor", "password")
        try:
            response = session.patch(
                "/folder/@constraints",
                json={"mode": "disabled"},
            )
            self.assertIn(response.status_code, (401, 403))
        finally:
            session.close()

    def test_patch_requires_modify_permission(self):
        api.user.create(
            email="member@example.com",
            username="member",
            password="password",
        )
        transaction.commit()
        session = RelativeSession(self.portal_url, test=self)
        session.headers.update({"Accept": "application/json"})
        session.auth = ("member", "password")
        try:
            response = session.patch(
                "/folder/@constraints",
                json={"mode": "disabled"},
            )
            self.assertIn(response.status_code, (401, 403))
        finally:
            session.close()

    def test_patch_rejects_types_user_cannot_add(self):
        api.user.create(
            email="contributor@example.com",
            username="contributor",
            password="password",
        )
        api.user.grant_roles(username="contributor", roles=["Contributor"])
        # Allow PATCH auth checks, but leave type-specific add perms restricted.
        self.portal.folder.manage_permission(
            "Modify portal content",
            roles=["Manager", "Site Administrator", "Contributor"],
            acquire=False,
        )
        self.portal.folder.manage_permission(
            "Modify constrain types",
            roles=["Manager", "Site Administrator", "Contributor"],
            acquire=False,
        )
        # Deny adding News Item for Contributor on this folder.
        self.portal.folder.manage_permission(
            "plone.app.contenttypes: Add News Item",
            roles=["Manager", "Site Administrator"],
            acquire=False,
        )
        transaction.commit()

        session = RelativeSession(self.portal_url, test=self)
        session.headers.update({"Accept": "application/json"})
        session.auth = ("contributor", "password")
        try:
            response = session.get("/folder/@constraints")
            self.assertEqual(response.status_code, 200)
            addable_ids = {item["id"] for item in response.json()["addable_types"]}
            self.assertNotIn("News Item", addable_ids)

            response = session.patch(
                "/folder/@constraints",
                json={
                    "mode": "enabled",
                    "locally_allowed_types": ["News Item"],
                    "immediately_addable_types": ["News Item"],
                },
            )
            self.assertEqual(response.status_code, 400)
        finally:
            session.close()
