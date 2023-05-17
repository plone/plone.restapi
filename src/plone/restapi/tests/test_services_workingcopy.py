from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_ITERATE_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestWorkingCopyEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_ITERATE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.portal.invokeFactory("Document", "document", title="Test Document")
        self.doc = self.portal.document

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_workingcopy_checkout(self):
        response = self.api_session.post(
            "/document/@workingcopy",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("@id", response.json())

        self.assertEqual(
            response.json()["@id"],
            f"{self.portal_url}/copy_of_document",
        )

    def test_workingcopy_get(self):
        # We create the working copy
        response = self.api_session.post(
            "/document/@workingcopy",
        )

        self.assertEqual(response.status_code, 201)

        # endpoint GET in the baseline object
        response = self.api_session.get(
            "/document/@workingcopy",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["working_copy"]["@id"],
            f"{self.portal_url}/copy_of_document",
        )
        self.assertEqual(
            response.json()["working_copy"]["creator_name"],
            "admin",
        )
        self.assertEqual(
            response.json()["working_copy"]["creator_url"],
            f"{self.portal_url}/author/admin",
        )

        # endpoint GET in the working_copy
        response = self.api_session.get(
            "/copy_of_document/@workingcopy",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["working_copy_of"]["@id"],
            f"{self.portal_url}/document",
        )
        self.assertEqual(
            response.json()["working_copy"]["@id"],
            f"{self.portal_url}/copy_of_document",
        )
        self.assertEqual(
            response.json()["working_copy"]["creator_name"],
            "admin",
        )
        self.assertEqual(
            response.json()["working_copy"]["creator_url"],
            f"{self.portal_url}/author/admin",
        )

        # Serialization on the baseline object
        response = self.api_session.get(
            "/document",
        )

        self.assertEqual(
            response.json()["working_copy"]["@id"],
            f"{self.portal_url}/copy_of_document",
        )
        self.assertEqual(
            response.json()["working_copy"]["creator_name"],
            "admin",
        )
        self.assertEqual(
            response.json()["working_copy"]["creator_url"],
            f"{self.portal_url}/author/admin",
        )
        self.assertEqual(response.json()["working_copy_of"], None)

        # Serialization on the working copy object
        response = self.api_session.get(
            "/copy_of_document",
        )
        self.assertEqual(
            response.json()["working_copy_of"]["@id"],
            f"{self.portal_url}/document",
        )
        self.assertEqual(
            response.json()["working_copy"]["@id"],
            f"{self.portal_url}/copy_of_document",
        )
        self.assertEqual(
            response.json()["working_copy"]["creator_name"],
            "admin",
        )
        self.assertEqual(
            response.json()["working_copy"]["creator_url"],
            f"{self.portal_url}/author/admin",
        )

    def test_workingcopy_notworkingcopy_get(self):
        # endpoint GET in the working_copy
        response = self.api_session.get(
            "/document/",
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.json()["working_copy_of"],
            None,
        )

    def test_workingcopy_delete_on_the_baseline(self):
        # We create the working copy
        response = self.api_session.post(
            "/document/@workingcopy",
        )
        self.assertEqual(response.status_code, 201)

        # Deleting in the baseline deletes the working copy
        response = self.api_session.delete(
            "/document/@workingcopy",
        )

        self.assertEqual(response.status_code, 204)

        response = self.api_session.get(
            "/copy_of_document",
        )
        self.assertEqual(response.status_code, 404)

    def test_workingcopy_delete_on_the_working_copy(self):
        # We create the working copy
        response = self.api_session.post(
            "/document/@workingcopy",
        )
        self.assertEqual(response.status_code, 201)

        # Deleting in the working copy deletes it too
        response = self.api_session.delete(
            "/copy_of_document/@workingcopy",
        )

        self.assertEqual(response.status_code, 204)

        response = self.api_session.get(
            "/copy_of_document",
        )
        self.assertEqual(response.status_code, 404)

    def test_workingcopy_patch_on_the_baseline(self):
        # We create the working copy
        response = self.api_session.post(
            "/document/@workingcopy",
        )
        self.assertEqual(response.status_code, 201)

        # Modify the working copy
        response = self.api_session.patch(
            "/copy_of_document", json={"title": "I just changed the title"}
        )

        # Checking in
        response = self.api_session.patch(
            "/document/@workingcopy",
        )

        # Check if the change is there
        response = self.api_session.get(
            "/document",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "I just changed the title")

    def test_workingcopy_patch_on_the_working_copy(self):
        # We create the working copy
        response = self.api_session.post(
            "/document/@workingcopy",
        )
        self.assertEqual(response.status_code, 201)

        # Modify the working copy
        response = self.api_session.patch(
            "/copy_of_document", json={"title": "I just changed the title"}
        )

        # Checking in
        response = self.api_session.patch(
            "/copy_of_document/@workingcopy",
        )

        # Check if the change is there
        response = self.api_session.get(
            "/document",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "I just changed the title")
