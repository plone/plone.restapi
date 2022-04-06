from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestRedirector(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_redirector(self):

        # create a document (doc)
        self.portal.invokeFactory("Document", id="doc", title="My Document")
        self.original_doc_url = self.portal.doc.absolute_url()
        transaction.commit()

        # move the document to a new place (doc -> new-doc)
        self.portal.manage_renameObject("doc", "new-doc")
        transaction.commit()

        # query the original document url returns the moved document
        response = self.api_session.get(self.original_doc_url)
        self.assertEqual("My Document", response.json().get("title"))

        # create a new document under the old location
        self.portal.invokeFactory(
            "Document", id="doc", title="New document under the old location"
        )
        transaction.commit()

        # query the original document url returns the moved document
        response = self.api_session.get(self.original_doc_url)
        self.assertEqual(
            "New document under the old location", response.json().get("title")
        )
