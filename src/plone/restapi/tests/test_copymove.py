from base64 import b64encode
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.testing import RelativeSession
from zope.event import notify
from ZPublisher.pubevents import PubStart

import transaction
import unittest


class TestCopyMove(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc1 = self.portal[
            self.portal.invokeFactory("Document", id="doc1", title="My Document")
        ]
        self.folder1 = self.portal[
            self.portal.invokeFactory("Folder", id="folder1", title="My Folder")
        ]

    def traverse(self, path="/plone", accept="application/json", method="GET"):
        request = self.layer["request"]
        request.environ["PATH_INFO"] = path
        request.environ["PATH_TRANSLATED"] = path
        request.environ["HTTP_ACCEPT"] = accept
        request.environ["REQUEST_METHOD"] = method
        auth = f"{SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        request._auth = "Basic %s" % b64encode(auth.encode("utf8")).decode("utf8")
        notify(PubStart(request))
        return request.traverse(path)

    def test_get_object_by_url(self):
        service = self.traverse("/plone/@copy", method="POST")
        obj = service.get_object(self.doc1.absolute_url())

        self.assertEqual(self.doc1, obj)

    def test_get_object_by_path(self):
        service = self.traverse("/plone/@copy", method="POST")
        obj = service.get_object("/doc1")

        self.assertEqual(self.doc1, obj)

    def test_get_object_by_uid(self):
        service = self.traverse("/plone/@copy", method="POST")
        obj = service.get_object(self.doc1.UID())

        self.assertEqual(self.doc1, obj)


class TestCopyMoveFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.doc1 = self.portal[
            self.portal.invokeFactory("Document", id="doc1", title="My Document")
        ]
        self.doc2 = self.portal[
            self.portal.invokeFactory("Document", id="doc2", title="My Document")
        ]
        self.folder1 = self.portal[
            self.portal.invokeFactory("Folder", id="folder1", title="My Folder")
        ]

        api.user.create(
            email="memberuser@example.com", username="memberuser", password="secret"
        )

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_copy_single_object(self):
        response = self.api_session.post(
            "/@copy", json={"source": self.doc1.absolute_url()}
        )
        transaction.commit()

        self.assertEqual(response.status_code, 200)
        self.assertIn("copy_of_doc1", self.portal.objectIds())

    def test_move_single_object(self):
        response = self.api_session.post(
            "/folder1/@move", json={"source": self.doc1.absolute_url()}
        )
        transaction.commit()

        self.assertEqual(response.status_code, 200)
        self.assertIn("doc1", self.folder1.objectIds())
        self.assertNotIn("doc1", self.portal.objectIds())

    def test_move_multiple_objects(self):
        response = self.api_session.post(
            "/folder1/@move",
            json={"source": [self.doc1.absolute_url(), self.doc2.absolute_url()]},
        )
        self.assertEqual(response.status_code, 200)
        transaction.commit()

        self.assertIn("doc1", self.folder1.objectIds())
        self.assertIn("doc2", self.folder1.objectIds())
        self.assertNotIn("doc1", self.portal.objectIds())
        self.assertNotIn("doc2", self.portal.objectIds())

    def test_copy_without_source_raises_400(self):
        response = self.api_session.post("/folder1/@copy")
        self.assertEqual(response.status_code, 400)

    def test_copy_not_existing_object(self):
        response = self.api_session.post("/@copy", json={"source": "does-not-exist"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([], response.json())

    def test_copy_multiple_objects(self):
        response = self.api_session.post(
            "/@copy",
            json={"source": [self.doc1.absolute_url(), self.doc2.absolute_url()]},
        )
        transaction.commit()

        self.assertEqual(response.status_code, 200)
        self.assertIn("copy_of_doc1", self.portal.objectIds())
        self.assertIn("copy_of_doc2", self.portal.objectIds())

    def test_copy_single_object_no_permissions_raises_403(self):
        self.api_session.auth = ("memberuser", "secret")
        response = self.api_session.post(
            "/@copy", json={"source": self.doc1.absolute_url()}
        )

        self.assertEqual(response.status_code, 403)

    def test_copy_single_object_no_auth_raises_401(self):
        self.api_session.auth = ("nonexistent", "secret")
        response = self.api_session.post(
            "/@copy", json={"source": self.doc1.absolute_url()}
        )

        self.assertEqual(response.status_code, 401)

    def test_move_single_object_no_permissions_raises_403(self):
        self.api_session.auth = ("memberuser", "secret")
        response = self.api_session.post(
            "/@move", json={"source": self.doc1.absolute_url()}
        )

        self.assertEqual(response.status_code, 403)

    def test_move_single_object_no_auth_raises_401(self):
        self.api_session.auth = ("nonexistent", "secret")
        response = self.api_session.post(
            "/@move", json={"source": self.doc1.absolute_url()}
        )

        self.assertEqual(response.status_code, 401)

    def test_move_single_object_no_permission_delete_source_raises_403(self):
        api.user.grant_roles(username="memberuser", obj=self.folder1, roles=["Manager"])
        api.content.transition(obj=self.doc1, transition="publish")
        transaction.commit()

        self.api_session.auth = ("memberuser", "secret")
        response = self.api_session.post(
            "/folder1/@move", json={"source": self.doc1.absolute_url()}
        )

        self.assertEqual(response.status_code, 403)
