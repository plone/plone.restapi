from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.interface import alsoProvides
from plone.app.testing import login


import transaction
import unittest


class TestServicesBreadcrumbs(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.folder = createContentInContainer(
            self.portal, "Folder", id="folder", title="Some Folder"
        )
        createContentInContainer(self.folder, "Document", id="doc1", title="A document")
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_breadcrumbs(self):
        response = self.api_session.get("/folder/doc1/@breadcrumbs")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "@id": self.portal_url + "/folder/doc1/@breadcrumbs",
                "root": self.portal_url,
                "items": [
                    {
                        "@id": self.portal_url + "/folder",
                        "title": "Some Folder",
                    },
                    {
                        "@id": self.portal_url + "/folder/doc1",
                        "title": "A document",
                    },
                ],
            },
        )


class TestServicesMultilingualBreadcrumbs(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.layer["request"]

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal["en"], "Document", title="Test document"
        )
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title="Test document"
        )
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        self.folder = createContentInContainer(
            self.portal["es"], "Folder", id="folder", title="Some Folder"
        )
        createContentInContainer(self.folder, "Document", id="doc1", title="A document")
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_breadcrumbs_multilingual(self):
        response = self.api_session.get("/es/folder/doc1/@breadcrumbs")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "@id": self.portal_url + "/es/folder/doc1/@breadcrumbs",
                "root": self.portal_url + "/es",
                "items": [
                    {
                        "@id": self.portal_url + "/es/folder",
                        "title": "Some Folder",
                    },
                    {
                        "@id": self.portal_url + "/es/folder/doc1",
                        "title": "A document",
                    },
                ],
            },
        )
