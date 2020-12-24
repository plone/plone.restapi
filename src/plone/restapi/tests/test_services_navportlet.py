# -*- coding: utf-8 -*-

from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.restapi.services.navigation.portlet import NavigationPortlet
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.CMFPlone.interfaces import INavigationSchema
from Products.CMFPlone.tests import dummy
from urllib.parse import urlencode
from zope.component import getUtility
from zope.interface import directlyProvides
from zope.interface import noLongerProvides

import transaction
import unittest


def opts(**kw):
    res = {}
    for k, v in kw.items():
        res["expand.navportlet." + k] = v

    return res


class TestServicesNavPortlet(unittest.TestCase):

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

        self.populateSite()
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def populateSite(self):
        """
        Portal
        +-doc1
        +-doc2
        +-doc3
        +-folder1
          +-doc11
          +-doc12
          +-doc13
        +-link1
        +-folder2
          +-doc21
          +-doc22
          +-doc23
          +-file21
          +-folder21
            +-doc211
            +-doc212
        """
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        if "Members" in self.portal:
            self.portal._delObject("Members")
            self.folder = None
        if "news" in self.portal:
            self.portal._delObject("news")
        if "events" in self.portal:
            self.portal._delObject("events")
        if "front-page" in self.portal:
            self.portal._delObject("front-page")
        if "folder" in self.portal:
            self.portal._delObject("folder")
        if "users" in self.portal:
            self.portal._delObject("users")

        self.portal.invokeFactory("Document", "doc1")
        self.portal.invokeFactory("Document", "doc2")
        self.portal.invokeFactory("Document", "doc3")
        self.portal.invokeFactory("Folder", "folder1")
        self.portal.invokeFactory("Link", "link1")
        self.portal.link1.remoteUrl = "http://plone.org"
        self.portal.link1.reindexObject()
        folder1 = getattr(self.portal, "folder1")
        folder1.invokeFactory("Document", "doc11")
        folder1.invokeFactory("Document", "doc12")
        folder1.invokeFactory("Document", "doc13")
        self.portal.invokeFactory("Folder", "folder2")
        folder2 = getattr(self.portal, "folder2")
        folder2.invokeFactory("Document", "doc21")
        folder2.invokeFactory("Document", "doc22")
        folder2.invokeFactory("Document", "doc23")
        folder2.invokeFactory("File", "file21")
        folder2.invokeFactory("Folder", "folder21")
        folder21 = getattr(folder2, "folder21")
        folder21.invokeFactory("Document", "doc211")
        folder21.invokeFactory("Document", "doc212")

        setRoles(self.portal, TEST_USER_ID, ["Member"])

    def renderer(self, context=None, data=None):
        context = context or self.portal
        request = self.layer["request"]
        request.form.update(data or {})
        return NavigationPortlet(context, request)

    def test_navportlet_with_no_params_gets_only_top_level(self):
        response = self.api_session.get("/folder1/@navportlet")

        self.assertEqual(response.status_code, 200)

        res = {
            "@id": "http://localhost:55001/plone/folder1/@navportlet",
            "has_custom_name": False,
            "items": [
                {
                    "@id": "http://localhost:55001/plone/folder1/doc11",
                    "description": "",
                    "href": "http://localhost:55001/plone/folder1/doc11",
                    "icon": "",
                    "is_current": False,
                    "is_folderish": False,
                    "is_in_path": False,
                    "items": [],
                    "normalized_id": "doc11",
                    "review_state": "private",
                    "thumb": "",
                    "title": "doc11",
                    "type": "document",
                },
                {
                    "@id": "http://localhost:55001/plone/folder1/doc12",
                    "description": "",
                    "href": "http://localhost:55001/plone/folder1/doc12",
                    "icon": "",
                    "is_current": False,
                    "is_folderish": False,
                    "is_in_path": False,
                    "items": [],
                    "normalized_id": "doc12",
                    "review_state": "private",
                    "thumb": "",
                    "title": "doc12",
                    "type": "document",
                },
                {
                    "@id": "http://localhost:55001/plone/folder1/doc13",
                    "description": "",
                    "href": "http://localhost:55001/plone/folder1/doc13",
                    "icon": "",
                    "is_current": False,
                    "is_folderish": False,
                    "is_in_path": False,
                    "items": [],
                    "normalized_id": "doc13",
                    "review_state": "private",
                    "thumb": "",
                    "title": "doc13",
                    "type": "document",
                },
            ],
            "title": "Navigation",
            "url": "http://localhost:55001/plone/sitemap",
        }

        self.assertEqual(
            response.json(),
            res,
        )

    def test_navportlet_with_no_params_gets_only_top_level_mixed_content(self):
        # With the context set to folder2 it should return a dict with
        # currentItem set to True
        response = self.api_session.get("/folder2/@navportlet")
        self.assertEqual(response.status_code, 200)

        res = {
            "@id": "http://localhost:55001/plone/folder2/@navportlet",
            "has_custom_name": False,
            "items": [
                {
                    "@id": "http://localhost:55001/plone/folder2/doc21",
                    "description": "",
                    "href": "http://localhost:55001/plone/folder2/doc21",
                    "icon": "",
                    "is_current": False,
                    "is_folderish": False,
                    "is_in_path": False,
                    "items": [],
                    "normalized_id": "doc21",
                    "review_state": "private",
                    "thumb": "",
                    "title": "doc21",
                    "type": "document",
                },
                {
                    "@id": "http://localhost:55001/plone/folder2/doc22",
                    "description": "",
                    "href": "http://localhost:55001/plone/folder2/doc22",
                    "icon": "",
                    "is_current": False,
                    "is_folderish": False,
                    "is_in_path": False,
                    "items": [],
                    "normalized_id": "doc22",
                    "review_state": "private",
                    "thumb": "",
                    "title": "doc22",
                    "type": "document",
                },
                {
                    "@id": "http://localhost:55001/plone/folder2/doc23",
                    "description": "",
                    "href": "http://localhost:55001/plone/folder2/doc23",
                    "icon": "",
                    "is_current": False,
                    "is_folderish": False,
                    "is_in_path": False,
                    "items": [],
                    "normalized_id": "doc23",
                    "review_state": "private",
                    "thumb": "",
                    "title": "doc23",
                    "type": "document",
                },
                {
                    "@id": "http://localhost:55001/plone/folder2/file21/view",
                    "description": "",
                    "href": "http://localhost:55001/plone/folder2/file21/view",
                    "icon": None,
                    "is_current": False,
                    "is_folderish": False,
                    "is_in_path": False,
                    "items": [],
                    "normalized_id": "file21",
                    "review_state": "",
                    "thumb": "",
                    "title": "file21",
                    "type": "file",
                },
                {
                    "@id": "http://localhost:55001/plone/folder2/folder21",
                    "description": "",
                    "href": "http://localhost:55001/plone/folder2/folder21",
                    "icon": "",
                    "is_current": False,
                    "is_folderish": True,
                    "is_in_path": False,
                    "items": [],
                    "normalized_id": "folder21",
                    "review_state": "private",
                    "thumb": "",
                    "title": "folder21",
                    "type": "folder",
                },
            ],
            "title": "Navigation",
            "url": "http://localhost:55001/plone/sitemap",
        }
        self.assertEqual(
            response.json(),
            res,
        )

        # self.assertTrue(tree)
        # self.assertEqual(tree["children"][-1]["currentItem"], True)

    def testHeadingLinkRooted(self):
        """
        See that heading link points to a content item if root selected,
        otherwise sitemap.
        """

        q = {
            "expand.navportlet.topLevel": 0,
            "expand.navportlet.root_path": "/".join(
                self.portal.folder2.getPhysicalPath()[2:]
            ),
        }
        qs = urlencode(q)

        response = self.api_session.get("/folder2/@navportlet?{}".format(qs))
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res["url"], "http://localhost:55001/plone/folder2")

    def testHeadingLinkRootedItemGone(self):
        """
        See that heading link points to a content item which do not exist
        """
        response = self.api_session.get(
            "/folder2/@navportlet",
            params={
                "expand.navportlet.topLevel": 0,
                "expand.navportlet.root_path": "/does/not/exist",
            },
        )
        res = response.json()
        # Points to the site root if the item is gone
        self.assertEqual(res["url"], "http://localhost:55001/plone/sitemap")

    def testHeadingLinkRootless(self):
        """
        See that heading link points to a global sitemap if no root item is set.
        """

        directlyProvides(self.portal.folder2, INavigationRoot)
        transaction.commit()
        response = self.api_session.get(
            "/folder2/@navportlet",
            params={"expand.navportlet.topLevel": 0},
        )
        link = response.json()["url"]
        # The root is not given -> should render the sitemap in the navigation root
        self.assertEqual(link, "http://localhost:55001/plone/folder2/sitemap")

        # # Even if the assignment contains no topLevel options and no self.root
        # # one should get link to the navigation root sitemap
        # view = self.renderer(
        #     self.portal.folder2.doc21, assignment=navigation.Assignment()
        # )
        response = self.api_session.get(
            "/folder2/doc21/@navportlet",
            params={},
        )
        link = response.json()["url"]
        # # The root is not given -> should render the sitemap in the navigation root
        self.assertEqual(link, "http://localhost:55001/plone/folder2/sitemap")

        response = self.api_session.get(
            "/folder1/@navportlet",
            params={"expand.navportlet.topLevel": 0},
        )
        link = response.json()["url"]
        # The root is not given -> should render the sitemap in the navigation root
        self.assertEqual(link, "http://localhost:55001/plone/sitemap")

        noLongerProvides(self.portal.folder2, INavigationRoot)
        transaction.commit()

    def testNavTreeExcludesItemsWithExcludeProperty(self):
        # Make sure that items with the exclude_from_nav property set get
        # no_display set to True

        self.portal.folder2.exclude_from_nav = True
        self.portal.folder2.reindexObject()

        transaction.commit()

        response = self.api_session.get(
            "@navportlet",
            params={
                "expand.navportlet.includeTop": True,
                "expand.navportlet.topLevel": 0,
                "expand.navportlet.bottomLevel": 0,
            },
        )
        tree = response.json()

        for c in tree["items"]:
            if c["href"] == "http://localhost:55001/plone/folder2":
                self.fail()

        self.portal.folder2.exclude_from_nav = False
        self.portal.folder2.reindexObject()
        transaction.commit()

    def testNavTreeExcludesDefaultPage(self):
        # Make sure that items which are the default page are excluded
        response = self.api_session.get(
            "/folder2/@navportlet",
            params={},
        )
        tree = response.json()
        self.assertTrue(
            [
                item
                for item in tree["items"]
                if item["href"] == "http://localhost:55001/plone/folder2/doc21"
            ]
        )

        self.portal.folder2.setDefaultPage("doc21")
        transaction.commit()

        response = self.api_session.get(
            "/folder2/@navportlet",
            params={},
        )
        tree = response.json()
        self.assertFalse(
            [
                item
                for item in tree["items"]
                if item["href"] == "http://localhost:55001/plone/folder2/doc21"
            ]
        )

        self.portal.folder2.setDefaultPage(None)
        transaction.commit()

    def testPortletsTitle(self):
        """If portlet's name is not explicitely specified we show
        default fallback 'Navigation', translate it and hide it
        with CSS."""
        response = self.api_session.get(
            "/@navportlet",
            params={},
        )
        tree = response.json()
        self.assertEqual(tree["title"], "Navigation")

        response = self.api_session.get(
            "/@navportlet",
            params={"expand.navportlet.name": "New navigation title"},
        )
        tree = response.json()
        self.assertEqual(tree["title"], "New navigation title")

    def testTopLevelTooDeep(self):

        view = self.renderer(self.portal, opts(topLevel=5))
        tree = view(expand=True)

        self.assertEqual(len(tree["navportlet"]["items"]), 0)

    def testShowAllParentsOverridesNavTreeExcludesItemsWithExcludeProperty(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property are not included
        self.portal.folder2.exclude_from_nav = True
        self.portal.folder2.reindexObject()
        view = self.renderer(
            self.portal.folder2.doc21, opts(includeTop=True, topLevel=0)
        )
        tree = view(expand=True)

        found = False

        for c in tree["navportlet"]["items"]:
            if c["href"] == "http://localhost:55001/plone/folder2":
                found = True
                break

        self.assertTrue(found)

    # # this test is not needed, we don't expose show_children
    # def testNavTreeMarksParentMetaTypesNotToQuery(self):
    #     # Make sure that items whose ids are in the idsNotToList navTree
    #     # property get no_display set to True
    #     view = self.renderer(self.portal.folder2.file21)
    #     tree = view(expand=True)
    #
    #     self.assertEqual(tree["navportlet"]["items"][-1]["show_children"], True)
    #
    #     registry = self.portal.portal_registry
    #     registry["plone.parent_types_not_to_query"] = [u"Folder"]
    #
    #     view = self.renderer(self.portal.folder2.file21)
    #     tree = view(expand=True)
    #
    #     self.assertEqual(tree["navportlet"]["items"][-1]["show_children"], False)

    def testCreateNavTreeWithLink(self):
        view = self.renderer(self.portal)
        tree = view(expand=True)["navportlet"]

        for child in tree["items"]:
            if child["portal_type"] != "Link":
                self.assertFalse(child["getRemoteUrl"])

            if child["Title"] == "link1":
                self.assertEqual(child["getRemoteUrl"], "http://plone.org")
                # as Creator, link1 should not use the remote Url
                self.assertFalse(child["useRemoteUrl"])

        self.portal.link1.setCreators(["some_other_user"])
        self.portal.link1.reindexObject()
        view = self.renderer(self.portal)
        tree = view(expand=True)["navportlet"]

        for child in tree["items"]:
            if child["portal_type"] != "Link":
                self.assertFalse(child["getRemoteUrl"])
            if child["Title"] == "link1":
                self.assertEqual(child["getRemoteUrl"], "http://plone.org")
                # as non-Creator user, link1 should use the remote Url
                self.assertTrue(child["useRemoteUrl"])

    def testNonStructuralFolderHidesChildren(self):
        # Make sure NonStructuralFolders act as if parent_types_not_to_query
        # is set.
        f = dummy.NonStructuralFolder("ns_folder")
        self.portal.folder1._setObject("ns_folder", f)
        self.portal.portal_catalog.reindexObject(self.portal.folder1.ns_folder)
        self.portal.portal_catalog.reindexObject(self.portal.folder1)
        view = self.renderer(
            self.portal.folder1.ns_folder, opts(includeTop=True, topLevel=0)
        )
        tree = view.getNavTree()
        self.assertEqual(
            tree["items"][3]["items"][3]["href"],
            "http://localhost:55001/plone/folder1/ns_folder",
        )
        self.assertEqual(len(tree["items"][3]["items"][3]["items"]), 0)

    def testTopLevel(self):
        view = self.renderer(self.portal.folder2.file21, opts(topLevel=1))
        tree = view.getNavTree()
        self.assertTrue(tree)

        self.assertEqual(
            tree["items"][-1]["href"],
            "http://localhost:55001/plone/folder2/folder21",
        )

    def testTopLevelWithContextAboveLevel(self):
        view = self.renderer(self.portal, opts(topLevel=1))
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["items"]), 0)

    def testIncludeTopWithoutNavigationRoot(self):
        view = self.renderer(
            self.portal.folder2.folder21,
            opts(topLevel=0, root_path=None, includeTop=True),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["items"]), 6)

        # self.assertTrue(view.root_is_portal())
        self.assertEqual(tree["url"], "http://localhost:55001/plone/sitemap")

    def testTopLevelWithNavigationRoot(self):
        # self.portal.folder2.invokeFactory("Folder", "folder21")
        # self.portal.folder2.folder21.invokeFactory("Document", "doc211")
        view = self.renderer(
            self.portal.folder2.folder21,
            opts(
                topLevel=1,
                root_path="/folder2"
                # self.portal.folder2.UID()
            ),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["items"]), 2)
        self.assertEqual(
            tree["items"][0]["href"],
            "http://localhost:55001/plone/folder2/folder21/doc211",
        )

    def testMultipleTopLevelWithNavigationRoot(self):
        # See bug 9405
        # http://dev.plone.org/plone/ticket/9405
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Folder", "abc")
        self.portal.invokeFactory("Folder", "abcde")
        self.portal.abc.invokeFactory("Folder", "down_abc")
        self.portal.abcde.invokeFactory("Folder", "down_abcde")

        view1 = self.renderer(
            self.portal.abc,
            opts(topLevel=0, root_path="/abc"),
        )
        view2 = self.renderer(
            self.portal.abc,
            opts(topLevel=0, root_path="/abcde"),
        )

        tree1 = view1.getNavTree()
        tree2 = view2.getNavTree()
        self.assertEqual(len(tree1["items"]), 1)
        self.assertEqual(len(tree2["items"]), 1)

        view1 = self.renderer(
            self.portal.abcde,
            opts(topLevel=0, root_path="/abc"),
        )

        view2 = self.renderer(
            self.portal.abcde,
            opts(topLevel=0, root_path="/abcde"),
        )

        tree1 = view1.getNavTree()
        tree2 = view2.getNavTree()

        self.assertEqual(len(tree2["items"]), 1)
        self.assertEqual(len(tree1["items"]), 1)

    def testShowAllParentsOverridesBottomLevel(self):
        view = self.renderer(
            self.portal.folder2.file21,
            opts(bottomLevel=1, topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        # Note: showAllParents makes sure we actually return items on the,
        # path to the context, but the portlet will not display anything
        # below bottomLevel.
        self.assertEqual(
            tree["items"][-1]["href"], "http://localhost:55001/plone/folder2"
        )
        # self.assertEqual(len(tree["items"][-1]["items"]), 1)
        # self.assertEqual(
        #     tree["items"][-1]["items"][0]["href"],
        #     "http://localhost:55001/plone/folder2/file21",
        # )

    def testBottomLevelStopsAtFolder(self):
        view = self.renderer(
            self.portal.folder2,
            opts(bottomLevel=1, topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree["items"][-1]["href"], "http://localhost:55001/plone/folder2"
        )
        self.assertEqual(len(tree["items"][-1]["items"]), 0)

    def testBottomLevelZeroNoLimit(self):
        """Test that bottomLevel=0 means no limit for bottomLevel."""

        # first we set a high integer as bottomLevel to simulate "no limit"
        view = self.renderer(
            self.portal.folder2,
            opts(bottomLevel=99, topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)

        self.assertEqual(
            tree["items"][-1]["items"][0]["href"],
            "http://localhost:55001/plone/folder2/doc21",
        )

        # now set bottomLevel to 0 -> outcome should be the same
        view = self.renderer(
            self.portal.folder2,
            opts(bottomLevel=0, topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree["items"][-1]["items"][0]["href"],
            "http://localhost:55001/plone/folder2/doc21",
        )

    def testBottomLevelZeroNoLimitRendering(self):
        """Test that bottomLevel=0 means no limit for bottomLevel."""

        # first we set a high integer as bottomLevel to simulate "no limit"
        view = self.renderer(
            self.portal.folder2,
            opts(bottomLevel=99, topLevel=0),
        )
        a = view(expand=True)

        # now set bottomLevel to 0 -> outcome should be the same
        view = self.renderer(
            self.portal.folder2,
            opts(bottomLevel=0, topLevel=0),
        )
        b = view(expand=True)

        self.assertEqual(a, b)

    def testNavRootWithUnicodeNavigationRoot(self):
        # self.portal.folder2.invokeFactory("Folder", "folder21")
        # self.portal.folder2.folder21.invokeFactory("Document", "doc211")
        view = self.renderer(
            self.portal.folder2.folder21,
            opts(
                topLevel=1,
                root_path="/folder2",
            ),
        )
        tree = view.getNavTree()
        self.assertEqual(tree["url"], "http://localhost:55001/plone/folder2/folder21")

    def testNoRootSet(self):
        view = self.renderer(
            self.portal.folder2.file21,
            opts(root_uid="", topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree["items"][-1]["href"], "http://localhost:55001/plone/folder2"
        )

    def testRootIsNotPortal(self):
        view = self.renderer(
            self.portal.folder2.file21,
            opts(root_path="/folder2", topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree["items"][0]["href"], "http://localhost:55001/plone/folder2/doc21"
        )

    def testRootDoesNotExist(self):
        view = self.renderer(
            self.portal.folder2.file21,
            opts(root_path="DOESNT_EXIST", topLevel=0),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["items"]), 6)

    def testAboveRoot(self):
        registry = getUtility(IRegistry)
        registry["plone.root"] = u"/folder2"
        view = self.renderer(self.portal)
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree["items"][0]["href"], "http://localhost:55001/plone/folder2/doc21"
        )

    def testOutsideRoot(self):
        view = self.renderer(
            self.portal.folder1,
            opts(root_path="/folder2"),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree["items"][0]["href"], "http://localhost:55001/plone/folder2/doc21"
        )

    def testRootIsCurrent(self):
        view = self.renderer(
            self.portal.folder2,
            opts(currentFolderOnly=True),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree["items"][0]["href"], "http://localhost:55001/plone/folder2/doc21"
        )

    def testRootIsCurrentWithFolderishDefaultPage(self):
        # self.portal.folder2.invokeFactory("Folder", "folder21")
        self.portal.folder2.setDefaultPage("folder21")

        view = self.renderer(
            self.portal.folder2.folder21,
            opts(currentFolderOnly=True),
        )
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree["items"][0]["href"], "http://localhost:55001/plone/folder2/doc21"
        )

    def testCustomQuery(self):
        # Try a custom query script for the navtree that returns only published
        # objects
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        workflow = self.portal.portal_workflow
        factory = self.portal.manage_addProduct["PythonScripts"]
        factory.manage_addPythonScript("getCustomNavQuery")
        script = self.portal.getCustomNavQuery
        script.ZPythonScript_edit("", 'return {"review_state": "published"}')

        self.assertEqual(self.portal.getCustomNavQuery(), {"review_state": "published"})

        view = self.renderer(self.portal.folder2, opts(topLevel=0))
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertTrue("items" in tree)

        # Should only contain current object
        self.assertEqual(len(tree["items"]), 1)  # different

        # change workflow for folder1
        workflow.doActionFor(self.portal.folder1, "publish")
        self.portal.folder1.reindexObject()

        view = self.renderer(self.portal.folder2, opts(topLevel=0))
        tree = view.getNavTree()
        # Should only contain current object and published folder
        self.assertEqual(len(tree["items"]), 2)

    def testStateFiltering(self):
        # Test Navtree workflow state filtering
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        registry = getUtility(IRegistry)
        navigation_settings = registry.forInterface(INavigationSchema, prefix="plone")
        workflow = self.portal.portal_workflow
        navigation_settings.workflow_states_to_show = ("published",)
        navigation_settings.filter_on_workflow = True

        view = self.renderer(self.portal.folder2, opts(topLevel=0))
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertTrue("items" in tree)

        # Should only contain current object
        self.assertEqual(len(tree["items"]), 1)

        # change workflow for folder1
        workflow.doActionFor(self.portal.folder1, "publish")
        self.portal.folder1.reindexObject()
        view = self.renderer(self.portal.folder2, opts(topLevel=0))
        tree = view.getNavTree()

        # Should only contain current object and published folder
        self.assertEqual(len(tree["items"]), 2)

    def testPrunedRootNode(self):
        # This test has been changed to conform to reality
        registry = self.portal.portal_registry
        registry["plone.parent_types_not_to_query"] = [u"Folder"]

        view = self.renderer(self.portal.folder1, opts(topLevel=0))
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["items"][4]["items"]), 0)

    def testPrunedRootNodeShowsAllParents(self):
        registry = self.portal.portal_registry
        registry["plone.parent_types_not_to_query"] = [u"Folder"]

        view = self.renderer(self.portal.folder1.doc11, opts(topLevel=1))
        tree = view.getNavTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree["items"]), 1)
        self.assertEqual(
            tree["items"][0]["href"], "http://localhost:55001/plone/folder1/doc11"
        )

    def testIsCurrentParentWithOverlapingNames(self):
        setRoles(
            self.portal,
            TEST_USER_ID,
            [
                "Manager",
            ],
        )
        self.portal.invokeFactory("Folder", "folder2x")
        self.portal.folder2x.invokeFactory("Document", "doc2x1")
        setRoles(
            self.portal,
            TEST_USER_ID,
            [
                "Member",
            ],
        )
        view = self.renderer(self.portal.folder2x.doc2x1, opts(topLevel=0))
        tree = view.getNavTree()
        self.assertTrue(tree)

        folder2x_node = [
            n for n in tree["items"] if n["href"].endswith("/plone/folder2x")
        ][0]
        self.assertTrue(folder2x_node["is_in_path"])

        folder2_node = [
            n for n in tree["items"] if n["href"].endswith("/plone/folder2")
        ][0]
        self.assertFalse(folder2_node["is_in_path"])


# def testPortletNotDisplayedOnINavigationRoot(self):
#     """test that navigation portlet does not show on INavigationRoot
#     folder
#     """
#     self.assertFalse(INavigationRoot.providedBy(self.portal.folder1))
#
#     # make folder1 as navigation root
#     directlyProvides(self.portal.folder1, INavigationRoot)
#     self.assertTrue(INavigationRoot.providedBy(self.portal.folder1))
#
#     # add nested subfolder in folder1
#     self.portal.folder1.invokeFactory("Folder", "folder1_1")
#
#     # make a navigation portlet
#     assignment = navigation.Assignment(bottomLevel=0, topLevel=1, root_uid=None)
#     portlet = self.renderer(self.portal.folder1, assignment=assignment)
#
#     # check there is no portlet
#     self.assertFalse(portlet.available)
#
# def testINavigationRootWithRelativeRootSet(self):
#     """test that navigation portlet uses relative root set by user
#     even in INavigationRoot case.
#     """
#     self.assertFalse(INavigationRoot.providedBy(self.portal.folder1))
#
#     # make folder1 as navigation root
#     directlyProvides(self.portal.folder1, INavigationRoot)
#     self.assertTrue(INavigationRoot.providedBy(self.portal.folder1))
#
#     # add two nested subfolders in folder1
#     self.portal.folder1.invokeFactory("Folder", "folder1_1")
#     self.portal.folder1.folder1_1.invokeFactory("Folder", "folder1_1_1")
#
#     # make a navigation portlet with navigation root set
#     assignment = navigation.Assignment(
#         bottomLevel=0, topLevel=0, root_uid=self.portal.folder1.folder1_1.UID()
#     )
#     portlet = self.renderer(self.portal.folder1.folder1_1, assignment=assignment)
#
#     # check there is a portlet
#     self.assertTrue(portlet.available)
#
#     # check that portlet root is actually the one specified
#     root = portlet.getNavRoot()
#     self.assertEqual(root.getId(), "folder1_1")
#
#     # check that portlet tree actually includes children
#     tree = portlet.getNavTree()
#     self.assertEqual(len(tree["children"]), 1)
#     self.assertEqual(
#         tree["children"][0]["item"].getPath(),
#         "/plone/folder1/folder1_1/folder1_1_1",
#     )
