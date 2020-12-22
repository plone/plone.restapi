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


class TestServicesNavigation(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
    maxDiff = None

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
        self.folder2 = createContentInContainer(
            self.portal, u"Folder", id=u"folder2", title=u"Some Folder 2"
        )
        self.subfolder1 = createContentInContainer(
            self.folder, u"Folder", id=u"subfolder1", title=u"SubFolder 1"
        )
        self.subfolder2 = createContentInContainer(
            self.folder, u"Folder", id=u"subfolder2", title=u"SubFolder 2"
        )
        self.thirdlevelfolder = createContentInContainer(
            self.subfolder1,
            u"Folder",
            id=u"thirdlevelfolder",
            title=u"Third Level Folder",
        )
        self.fourthlevelfolder = createContentInContainer(
            self.thirdlevelfolder,
            u"Folder",
            id=u"fourthlevelfolder",
            title=u"Fourth Level Folder",
        )
        createContentInContainer(
            self.folder, u"Document", id=u"doc1", title=u"A document"
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_navportlet_with_no_params_gets_only_top_level(self):
        response = self.api_session.get("/folder/@navportlet")

        self.assertEqual(response.status_code, 200)

        res = {
            "@id": "http://localhost:55001/plone/folder/@navportlet",
            "has_custom_name": False,
            "items": [
                {
                    "@id": "http://localhost:55001/plone/folder/subfolder1",
                    "description": "",
                    "href": "http://localhost:55001/plone/folder/subfolder1",
                    "icon": "",
                    "is_current": False,
                    "is_folderish": True,
                    "is_in_path": False,
                    "items": [],
                    "normalized_id": "subfolder1",
                    "review_state": "private",
                    "thumb": "",
                    "title": "SubFolder 1",
                    "type": "folder",
                },
                {
                    "@id": "http://localhost:55001/plone/folder/subfolder2",
                    "description": "",
                    "href": "http://localhost:55001/plone/folder/subfolder2",
                    "icon": "",
                    "is_current": False,
                    "is_folderish": True,
                    "is_in_path": False,
                    "items": [],
                    "normalized_id": "subfolder2",
                    "review_state": "private",
                    "thumb": "",
                    "title": "SubFolder 2",
                    "type": "folder",
                },
                {
                    "@id": "http://localhost:55001/plone/folder/doc1",
                    "description": "",
                    "href": "http://localhost:55001/plone/folder/doc1",
                    "icon": "",
                    "is_current": False,
                    "is_folderish": False,
                    "is_in_path": False,
                    "items": [],
                    "normalized_id": "doc1",
                    "review_state": "private",
                    "thumb": "",
                    "title": "A document",
                    "type": "document",
                },
            ],
            "title": None,
            "url": "http://localhost:55001/plone/sitemap",
        }

        self.assertEqual(
            response.json(),
            res,
        )

    # def test_navigation_service(self):
    #     response = self.api_session.get(
    #         "/folder/@navigation", params={"expand.navigation.depth": 2}
    #     )
    #
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.json()["items"]), 3)
    #     self.assertEqual(response.json()["items"][1]["title"], u"Some Folder")
    #     self.assertEqual(len(response.json()["items"][1]["items"]), 3)
    #     self.assertEqual(len(response.json()["items"][2]["items"]), 0)
    #
    #     response = self.api_session.get(
    #         "/folder/@navigation", params={"expand.navigation.depth": 3}
    #     )
    #
    #     self.assertEqual(len(response.json()["items"][1]["items"][0]["items"]), 1)
    #     self.assertEqual(
    #         response.json()["items"][1]["items"][0]["items"][0]["title"],
    #         u"Third Level Folder",
    #     )
    #     self.assertNotIn("items", response.json()["items"][1]["items"][0]["items"][0])
    #
    #     response = self.api_session.get(
    #         "/folder/@navigation", params={"expand.navigation.depth": 4}
    #     )
    #
    #     self.assertEqual(
    #         len(response.json()["items"][1]["items"][0]["items"][0]["items"]), 1
    #     )
    #     self.assertEqual(
    #         response.json()["items"][1]["items"][0]["items"][0]["items"][0][
    #             "title"
    #         ],  # noqa
    #         u"Fourth Level Folder",
    #     )
