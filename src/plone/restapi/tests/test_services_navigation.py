"""
Test Rest API endpoints for retrieving navigation breadcrumbs.
"""

from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from plone.restapi import testing
from Products.CMFPlone.interfaces.controlpanel import INavigationSchema
from zope.component import getUtility

import transaction


class TestServicesNavigation(testing.PloneRestAPIBrowserTestCase):
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
        self.folder2 = createContentInContainer(
            self.portal, "Folder", id="folder2", title="Some Folder 2"
        )
        self.subfolder1 = createContentInContainer(
            self.folder, "Folder", id="subfolder1", title="SubFolder 1"
        )
        self.subfolder2 = createContentInContainer(
            self.folder, "Folder", id="subfolder2", title="SubFolder 2"
        )
        self.thirdlevelfolder = createContentInContainer(
            self.subfolder1,
            "Folder",
            id="thirdlevelfolder",
            title="Third Level Folder",
        )
        self.fourthlevelfolder = createContentInContainer(
            self.thirdlevelfolder,
            "Folder",
            id="fourthlevelfolder",
            title="Fourth Level Folder",
        )
        createContentInContainer(self.folder, "Document", id="doc1", title="A document")
        transaction.commit()

    def test_navigation_service(self):
        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 3)
        self.assertEqual(response.json()["items"][1]["title"], "Some Folder")
        self.assertEqual(len(response.json()["items"][1]["items"]), 3)
        self.assertEqual(len(response.json()["items"][2]["items"]), 0)

        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 3}
        )

        self.assertEqual(len(response.json()["items"][1]["items"][0]["items"]), 1)
        self.assertEqual(
            response.json()["items"][1]["items"][0]["items"][0]["title"],
            "Third Level Folder",
        )
        self.assertEqual(
            len(response.json()["items"][1]["items"][0]["items"][0]["items"]),
            0,
        )

        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 4}
        )

        self.assertEqual(
            len(response.json()["items"][1]["items"][0]["items"][0]["items"]),
            1,
        )
        self.assertEqual(
            response.json()["items"][1]["items"][0]["items"][0]["items"][0][
                "title"
            ],  # noqa
            "Fourth Level Folder",
        )

    def test_dont_broke_with_contents_without_review_state(self):
        createContentInContainer(
            self.portal,
            "File",
            id="example-file",
            title="Example file",
        )
        createContentInContainer(
            self.folder,
            "File",
            id="example-file-1",
            title="Example file 1",
        )
        transaction.commit()

        response = self.api_session.get("/folder/@navigation")
        self.assertIsNone(response.json()["items"][3]["review_state"])

        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        )
        self.assertIsNone(response.json()["items"][1]["items"][3]["review_state"])

    def test_navigation_sorting(self):
        createContentInContainer(
            self.portal,
            "File",
            id="example-file",
            title="Example file",
        )
        createContentInContainer(
            self.folder,
            "File",
            id="example-file-1",
            title="Example file 1",
        )
        transaction.commit()
        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        ).json()

        contents = response["items"][1]["items"]
        self.assertEqual(
            [p["@id"].replace(self.portal.absolute_url(), "") for p in contents],
            [
                "/folder/subfolder1",
                "/folder/subfolder2",
                "/folder/doc1",
                "/folder/example-file-1",
            ],
        )

        self.portal["folder"].moveObjectsUp(["example-file-1"])
        transaction.commit()
        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        ).json()
        contents = response["items"][1]["items"]
        self.assertEqual(
            [p["@id"].replace(self.portal.absolute_url(), "") for p in contents],
            [
                "/folder/subfolder1",
                "/folder/subfolder2",
                "/folder/example-file-1",
                "/folder/doc1",
            ],
        )

    def test_use_nav_title_when_available_and_set(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        displayed_types = settings.displayed_types
        settings.displayed_types = tuple(list(displayed_types) + ["DXTestDocument"])

        title = "Example Document"
        nav_title = "Fancy title"

        createContentInContainer(
            self.folder,
            "DXTestDocument",
            id="example-dx-document",
            title=title,
            nav_title=nav_title,
        )
        transaction.commit()

        response = self.api_session.get(
            "/folder/@navigation", params={"expand.navigation.depth": 2}
        )

        self.assertEqual(response.json()["items"][1]["items"][-1]["title"], nav_title)
