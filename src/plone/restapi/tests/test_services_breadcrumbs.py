# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestServicesBreadcrumbs(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.folder = createContentInContainer(
            self.portal, u"Folder", id=u"folder", title=u"Some Folder"
        )
        createContentInContainer(
            self.folder, u"Document", id=u"doc1", title=u"A document"
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_breadcrumbs(self):
        response = self.api_session.get("/folder/doc1/@breadcrumbs")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "@id": self.portal_url + u"/folder/doc1/@breadcrumbs",
                "items": [
                    {u"@id": self.portal_url + u"/folder", u"title": u"Some Folder"},
                    {
                        u"@id": self.portal_url + u"/folder/doc1",
                        u"title": u"A document",
                    },
                ],
            },
        )
