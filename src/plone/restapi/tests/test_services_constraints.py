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
        self.assertEqual(data["mode"], "disabled")
        self.assertIn("Document", data["locally_allowed_types"])
        self.assertIn("Document", data["immediately_addable_types"])
        self.assertEqual(data["@id"], f"{self.portal_url}/folder/@constraints")

    def test_get_document_is_not_configurable(self):
        response = self.api_session.get("/doc/@constraints")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["configurable"])
        self.assertIsNone(data["mode"])
        self.assertEqual(data["locally_allowed_types"], [])
        self.assertEqual(data["immediately_addable_types"], [])

    def test_patch_enabled_constraints(self):
        response = self.api_session.patch(
            "/folder/@constraints",
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

    def test_patch_updates_effective_types(self):
        response = self.api_session.patch(
            "/folder/@constraints",
            json={
                "mode": "enabled",
                "locally_allowed_types": ["Image", "File"],
                "immediately_addable_types": ["Image"],
            },
        )
        self.assertEqual(response.status_code, 200)
        transaction.commit()

        types = self.api_session.get("/folder/@types").json()
        addable = {item["id"] for item in types if item["addable"]}
        immediately = {item["id"] for item in types if item["immediately_addable"]}
        self.assertEqual(addable, {"Image", "File"})
        self.assertEqual(immediately, {"Image"})

    def test_patch_acquire_mode(self):
        self.portal.folder.invokeFactory("Folder", id="child", title="Child")
        transaction.commit()
        response = self.api_session.patch(
            "/folder/child/@constraints",
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
