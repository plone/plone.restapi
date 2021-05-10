# -*- coding: utf-8 -*-
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

        self.api_session = RelativeSession(self.portal_url)
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

        self.assertEquals(
            response.json()["@id"],
            "{}/copy_of_document".format(self.portal_url),
        )

    def test_workingcopy_get(self):
        response = self.api_session.post(
            "/document/@workingcopy",
        )

        self.assertEqual(response.status_code, 201)

        response = self.api_session.get(
            "/document/@workingcopy",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("@id", response.json())

        self.assertEquals(
            response.json()["@id"],
            "{}/copy_of_document".format(self.portal_url),
        )

        # Serialization on the baseline object
        response = self.api_session.get(
            "/document",
        )

        self.assertEquals(
            response.json()["working_copy"]["@id"],
            "{}/copy_of_document".format(self.portal_url),
        )
        self.assertEquals(
            response.json()["working_copy"]["creator_name"],
            "admin",
        )
        self.assertEquals(
            response.json()["working_copy"]["creator_url"],
            "{}/author/admin".format(self.portal_url),
        )
        self.assertEquals(response.json()["working_copy_of"], None)

        # Serialization on the working copy object
        response = self.api_session.get(
            "/copy_of_document",
        )
        self.assertEquals(
            response.json()["working_copy_of"]["@id"],
            "{}/document".format(self.portal_url),
        )
        self.assertEquals(
            response.json()["working_copy"]["@id"],
            "{}/copy_of_document".format(self.portal_url),
        )
        self.assertEquals(
            response.json()["working_copy"]["creator_name"],
            "admin",
        )
        self.assertEquals(
            response.json()["working_copy"]["creator_url"],
            "{}/author/admin".format(self.portal_url),
        )
