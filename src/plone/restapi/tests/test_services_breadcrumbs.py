"""
Test Rest API endpoints for retrieving navigation breadcrumbs.
"""

from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.dexterity.utils import createContentInContainer
from plone.restapi import testing
from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING
from zope.interface import alsoProvides

import transaction


class TestServicesBreadcrumbs(testing.PloneRestAPIBrowserTestCase):
    """
    Test Rest API endpoints for retrieving navigation breadcrumbs.
    """

    def setUp(self):
        """
        Create content to test against.
        """
        super().setUp()

        self.folder = createContentInContainer(
            self.portal, "Folder", id="folder", title="Some Folder"
        )
        createContentInContainer(self.folder, "Document", id="doc1", title="A document")
        transaction.commit()

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


class TestServicesMultilingualBreadcrumbs(testing.PloneRestAPIBrowserTestCase):
    """
    Test Rest API endpoints for retrieving navigation breadcrumbs.
    """

    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        """
        Create content to test against.
        """
        super().setUp()

        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
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
