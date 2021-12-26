from datetime import date
from DateTime import DateTime
from pkg_resources import get_distribution
from pkg_resources import parse_version
from plone import api
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.restapi.tests.helpers import result_paths
from plone.uuid.interfaces import IMutableUUID
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

import transaction
import unittest


HAS_PLONE_6 = parse_version(
    get_distribution("Products.CMFPlone").version
) >= parse_version("6.0.0a1")


class TestSearchFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST
        self.catalog = getToolByName(self.portal, "portal_catalog")

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        api.user.create(
            email="editor@example.com",
            username="editoruser",
            password="secret",
        )
        api.user.create(
            email="editor@example.com",
            username="localeditor",
            password="secret",
        )

        # /plone/folder
        self.folder = createContentInContainer(
            self.portal, "Folder", id="folder", title="Some Folder"
        )
        api.user.grant_roles(username="editoruser", roles=["Editor"])
        api.user.grant_roles(
            username="localeditor", obj=self.folder, roles=["Editor", "Reader"]
        )

        # /plone/folder/doc
        self.doc = createContentInContainer(
            self.folder,
            "DXTestDocument",
            id="doc",
            title="Lorem Ipsum",
            start=DateTime(1950, 1, 1, 0, 0),
            effective=DateTime(1995, 1, 1, 0, 0),
            expires=DateTime(1999, 1, 1, 0, 0),
            test_int_field=42,
            test_list_field=["Keyword1", "Keyword2", "Keyword3"],
            test_bool_field=True,
            test_richtext_field=RichTextValue(
                raw="<p>Some Text</p>",
                mimeType="text/html",
                outputMimeType="text/html",
            ),
        )
        IMutableUUID(self.doc).set("77779ffa110e45afb1ba502f75f77777")
        self.doc.reindexObject()

        # /plone/folder/other-document
        self.doc2 = createContentInContainer(
            self.folder,
            "DXTestDocument",
            id="other-document",
            title="Other Document",
            description="\xdcbersicht",
            start=DateTime(1975, 1, 1, 0, 0),
            effective=DateTime(2015, 1, 1, 0, 0),
            expires=DateTime(2020, 1, 1, 0, 0),
            test_list_field=["Keyword2", "Keyword3"],
            test_bool_field=False,
        )

        # /plone/folder2
        self.folder2 = createContentInContainer(
            self.portal, "Folder", id="folder2", title="Another Folder"
        )

        # /plone/folder2/doc
        createContentInContainer(
            self.folder2,
            "DXTestDocument",
            id="doc",
            title="Document in second folder",
            start=DateTime(1975, 1, 1, 0, 0),
            effective=DateTime(2015, 1, 1, 0, 0),
            expires=DateTime(2020, 1, 1, 0, 0),
            test_bool_field=False,
        )

        # /plone/doc-outside-folder
        createContentInContainer(
            self.portal,
            "DXTestDocument",
            id="doc-outside-folder",
            title="Doc outside folder",
        )

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_overall_response_format(self):
        response = self.api_session.get("/@search")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        results = response.json()
        self.assertEqual(
            results["items_total"],
            len(results["items"]),
            "items_total property should match actual item count.",
        )

    def test_search_on_context_constrains_query_by_path(self):
        response = self.api_session.get("/folder/@search")
        self.assertSetEqual(
            {"/plone/folder", "/plone/folder/doc", "/plone/folder/other-document"},
            set(result_paths(response.json())),
        )

    def test_search_in_vhm(self):
        # Install a Virtual Host Monster
        if "virtual_hosting" not in self.app.objectIds():
            # If ZopeLite was imported, we have no default virtual
            # host monster
            from Products.SiteAccess.VirtualHostMonster import (
                manage_addVirtualHostMonster,
            )

            manage_addVirtualHostMonster(self.app, "virtual_hosting")
        transaction.commit()

        # we don't get a result if we do not provide the full physical path
        response = self.api_session.get("/@search?path=/folder")
        self.assertSetEqual(set(), set(result_paths(response.json())))

        # If we go through the VHM will will get results if we only use
        # the part of the path inside the VHM
        vhm_url = "{}/VirtualHostBase/http/plone.org/plone/VirtualHostRoot/{}".format(
            self.app.absolute_url(),
            "@search?path=/folder",
        )
        response = self.api_session.get(vhm_url)
        self.assertSetEqual(
            {"/folder", "/folder/doc", "/folder/other-document"},
            set(result_paths(response.json())),
        )

    def test_search_in_vhm_multiple_paths(self):
        # Install a Virtual Host Monster
        if "virtual_hosting" not in self.app.objectIds():
            # If ZopeLite was imported, we have no default virtual
            # host monster
            from Products.SiteAccess.VirtualHostMonster import (
                manage_addVirtualHostMonster,
            )

            manage_addVirtualHostMonster(self.app, "virtual_hosting")
        transaction.commit()

        # path as a list
        query = {"path": ["/folder", "/folder2"]}

        # If we go through the VHM we will get results for multiple paths
        # if we only use the part of the path inside the VHM
        vhm_url = "{}/VirtualHostBase/http/plone.org/plone/VirtualHostRoot/{}".format(
            self.app.absolute_url(),
            "@search",
        )
        response = self.api_session.get(vhm_url, params=query)
        self.assertSetEqual(
            {
                "/folder",
                "/folder/doc",
                "/folder/other-document",
                "/folder2",
                "/folder2/doc",
            },
            set(result_paths(response.json())),
        )

        # path as a dict with a query list
        query = {"path.query": ["/folder", "/folder2"]}

        # If we go through the VHM we will get results for multiple paths
        # if we only use the part of the path inside the VHM
        vhm_url = "{}/VirtualHostBase/http/plone.org/plone/VirtualHostRoot/{}".format(
            self.app.absolute_url(),
            "@search",
        )
        response = self.api_session.get(vhm_url, params=query)
        self.assertSetEqual(
            {
                "/folder",
                "/folder/doc",
                "/folder/other-document",
                "/folder2",
                "/folder2/doc",
            },
            set(result_paths(response.json())),
        )

    def test_path_gets_prefilled_if_missing_from_path_query_dict(self):
        response = self.api_session.get("/@search?path.depth=1")
        self.assertSetEqual(
            {"/plone/folder", "/plone/folder2", "/plone/doc-outside-folder"},
            set(result_paths(response.json())),
        )

    def test_partial_metadata_retrieval(self):
        query = {
            "SearchableText": "lorem",
            "metadata_fields": ["portal_type", "review_state"],
        }
        response = self.api_session.get("/@search", params=query)

        self.assertDictContainsSubset(
            {
                "@id": self.portal_url + "/folder/doc",
                "title": "Lorem Ipsum",
                "portal_type": "DXTestDocument",
                "review_state": "private",
            },
            response.json()["items"][0],
        )

    def test_full_metadata_retrieval(self):
        query = {"SearchableText": "lorem", "metadata_fields": "_all"}
        response = self.api_session.get("/@search", params=query)

        first_item = response.json()["items"][0]
        self.assertLessEqual(
            {
                "@id": self.portal_url + "/folder/doc",
                "Creator": "test_user_1_",
                "Description": "",
                "EffectiveDate": "None",
                "ExpirationDate": "None",
                "Subject": [],
                "Title": "Lorem Ipsum",
                "Type": "DX Test Document",
                "UID": "77779ffa110e45afb1ba502f75f77777",
                "author_name": None,
                "cmf_uid": None,
                "commentators": [],
                "description": "",
                "effective": "1995-01-01T00:00:00+00:00",
                "end": None,
                "exclude_from_nav": False,
                "expires": "1999-01-01T00:00:00+00:00",
                "getId": "doc",
                "getPath": "/plone/folder/doc",
                "getRemoteUrl": None,
                "getURL": self.portal_url + "/folder/doc",
                "id": "doc",
                "in_response_to": None,
                "is_folderish": False,
                "last_comment_date": None,
                "listCreators": ["test_user_1_"],
                "location": None,
                "portal_type": "DXTestDocument",
                "review_state": "private",
                "start": "1950-01-01T00:00:00+00:00",
                "sync_uid": None,
                "title": "Lorem Ipsum",
                "total_comments": 0,
            }.items(),
            first_item.items(),
        )
        # This value changed in Plone 5.2
        # (Dexterity gained support for getObjSize)
        self.assertIn(first_item["getObjSize"], ("0 KB", "1 KB"))

    def test_full_objects_retrieval(self):
        query = {
            "SearchableText": "lorem",
            "metadata_fields": ["portal_type", "review_state"],
            "fullobjects": True,
        }
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(
            "<p>Some Text</p>",
            response.json()["items"][0]["test_richtext_field"]["data"],
        )
        self.assertEqual(
            self.portal_url + "/folder/doc", response.json()["items"][0]["@id"]
        )

    def test_full_objects_retrieval_discussion(self):
        # Allow discussion
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        self.doc.allow_discussion = True

        transaction.commit()

        url = f"{self.doc.absolute_url()}/@comments"
        self.api_session.post(url, json={"text": "comment 1"})
        transaction.commit()

        query = {"portal_type": "Discussion Item", "fullobjects": True}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_full_objects_retrieval_collections(self):
        self.collection = createContentInContainer(
            self.folder, "Collection", id="collection"
        )
        transaction.commit()

        query = {"portal_type": "Collection", "fullobjects": True}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_search_orphan_brain(self):

        # prevent unindex when deleting self.doc
        old__unindexObject = self.doc.__class__.unindexObject
        self.doc.__class__.unindexObject = lambda *args: None
        self.doc.aq_parent.manage_delObjects([self.doc.getId()])
        self.doc.__class__.unindexObject = old__unindexObject
        # doc deleted but still in portal_catalog
        doc_uid = self.doc.UID()
        self.assertFalse(self.doc in self.doc.aq_parent)
        self.assertTrue(self.portal.portal_catalog(UID=doc_uid))
        transaction.commit()

        # query with fullobjects
        query = {"portal_type": "DXTestDocument", "fullobjects": True, "UID": doc_uid}
        response = self.api_session.get("/@search", params=query)
        self.assertEqual(response.status_code, 200, response.content)
        results = response.json()
        self.assertEqual(len(results["items"]), 0)

        # query without fullobjects
        query = {"portal_type": "DXTestDocument", "UID": doc_uid}
        response = self.api_session.get("/@search", params=query)
        self.assertEqual(response.status_code, 200, response.content)
        results = response.json()
        self.assertEqual(len(results["items"]), 1)

    # ZCTextIndex

    def test_fulltext_search(self):
        query = {"SearchableText": "lorem"}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(["/plone/folder/doc"], result_paths(response.json()))

    def test_fulltext_search_with_non_ascii_characters(self):
        query = {"SearchableText": "\xfcbersicht"}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(
            ["/plone/folder/other-document"], result_paths(response.json())
        )

    # KeywordIndex

    def test_keyword_index_str_query(self):
        query = {"test_list_field": "Keyword1"}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(["/plone/folder/doc"], result_paths(response.json()))

    def test_keyword_index_str_query_or(self):
        query = {"test_list_field": ["Keyword2", "Keyword3"]}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(
            ["/plone/folder/doc", "/plone/folder/other-document"],
            result_paths(response.json()),
        )

    def test_keyword_index_str_query_and(self):
        query = {
            "test_list_field.query": ["Keyword1", "Keyword2"],
            "test_list_field.operator": "and",
        }
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(["/plone/folder/doc"], result_paths(response.json()))

    # BooleanIndex

    def test_boolean_index_query(self):
        query = {"test_bool_field": True, "portal_type": "DXTestDocument"}
        response = self.api_session.get("/folder/@search", params=query)
        self.assertEqual(["/plone/folder/doc"], result_paths(response.json()))

        query = {"test_bool_field": False, "portal_type": "DXTestDocument"}
        response = self.api_session.get("/folder/@search", params=query)
        self.assertEqual(
            ["/plone/folder/other-document"], result_paths(response.json())
        )

    # FieldIndex

    def test_field_index_int_query(self):
        query = {"test_int_field:int": 42}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(["/plone/folder/doc"], result_paths(response.json()))

    def test_field_index_int_range_query(self):
        query = {
            "test_int_field.query:int": [41, 43],
            "test_int_field.range": "min:max",
        }
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(["/plone/folder/doc"], result_paths(response.json()))

    # ExtendedPathIndex

    def test_extended_path_index_query(self):
        query = {"path": "/".join(self.folder.getPhysicalPath())}

        response = self.api_session.get("/@search", params=query)

        self.assertEqual(
            sorted(
                [
                    "/plone/folder",
                    "/plone/folder/doc",
                    "/plone/folder/other-document",
                ]
            ),
            sorted(result_paths(response.json())),
        )

    def test_extended_path_index_query_multiple(self):
        # path as a list
        query = {
            "path": [
                "/".join(self.folder.getPhysicalPath()),
                "/".join(self.folder2.getPhysicalPath()),
            ]
        }
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(
            sorted(
                [
                    "/plone/folder",
                    "/plone/folder/doc",
                    "/plone/folder/other-document",
                    "/plone/folder2",
                    "/plone/folder2/doc",
                ]
            ),
            sorted(result_paths(response.json())),
        )

        # path as a dict with a query list
        query = {
            "path.query": [
                "/".join(self.folder.getPhysicalPath()),
                "/".join(self.folder2.getPhysicalPath()),
            ]
        }
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(
            sorted(
                [
                    "/plone/folder",
                    "/plone/folder/doc",
                    "/plone/folder/other-document",
                    "/plone/folder2",
                    "/plone/folder2/doc",
                ]
            ),
            sorted(result_paths(response.json())),
        )

    def test_extended_path_index_depth_limiting(self):
        lvl1 = createContentInContainer(self.portal, "Folder", id="lvl1")
        lvl2 = createContentInContainer(lvl1, "Folder", id="lvl2")
        createContentInContainer(lvl2, "Folder", id="lvl3")
        transaction.commit()

        path = "/plone/lvl1"

        # Depth 0 - only object identified by path
        query = {"path.query": path, "path.depth": 0}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(["/plone/lvl1"], result_paths(response.json()))

        # Depth 1 - immediate children
        query = {"path.query": path, "path.depth": 1}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(["/plone/lvl1/lvl2"], result_paths(response.json()))

        # No depth - object itself and all children
        query = {"path": path}
        response = self.api_session.get("/@search", params=query)

        self.assertSetEqual(
            {"/plone/lvl1", "/plone/lvl1/lvl2", "/plone/lvl1/lvl2/lvl3"},
            set(result_paths(response.json())),
        )

    # DateIndex

    def test_date_index_query(self):
        query = {"start": date(1950, 1, 1).isoformat()}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(["/plone/folder/doc"], result_paths(response.json()))

    def test_date_index_ranged_query(self):
        query = {
            "start.query": [date(1949, 1, 1).isoformat(), date(1951, 1, 1).isoformat()],
            "start.range": "min:max",
        }
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(["/plone/folder/doc"], result_paths(response.json()))

    # DateRangeIndex

    def test_date_range_index_query(self):
        query = {"effectiveRange": date(1997, 1, 1).isoformat()}
        response = self.api_session.get("/folder/@search", params=query)

        self.assertEqual(2, len(result_paths(response.json())))
        self.assertTrue("/plone/folder" in result_paths(response.json()))
        self.assertTrue("/plone/folder/doc" in result_paths(response.json()))

    # DateRecurringIndex

    def test_date_recurring_index_query(self):
        from datetime import datetime

        createContentInContainer(
            self.folder,
            "Event",
            id="event",
            title="Event",
            start=datetime(2013, 1, 1, 0, 0),
            end=datetime(2013, 1, 1, 23, 59),
            whole_day=True,
            recurrence="FREQ=DAILY;COUNT=10;INTERVAL=2",
            timezone="UTC",
        )
        import transaction

        transaction.commit()

        # First occurrence
        query = {"start": date(2013, 1, 1).isoformat()}
        response = self.api_session.get("/folder/@search", params=query)

        self.assertEqual(["/plone/folder/event"], result_paths(response.json()))

        # No event that day
        query = {"start": date(2013, 1, 2).isoformat()}
        response = self.api_session.get("/folder/@search", params=query)

        self.assertEqual([], result_paths(response.json()))

        # Second occurrence
        query = {"start": date(2013, 1, 3).isoformat()}
        response = self.api_session.get("/folder/@search", params=query)

        self.assertEqual(["/plone/folder/event"], result_paths(response.json()))

        # Ranged query
        query = {
            "start.query": [date(2013, 1, 1).isoformat(), date(2013, 1, 5).isoformat()],
            "start.range": "min:max",
        }
        response = self.api_session.get("/folder/@search", params=query)

        self.assertEqual(["/plone/folder/event"], result_paths(response.json()))

    # UUIDIndex

    def test_uuid_index_query(self):
        IMutableUUID(self.doc).set("7777a074cb4240d08c9a129e3a837777")
        self.doc.reindexObject()
        transaction.commit()

        query = {"UID": "7777a074cb4240d08c9a129e3a837777"}
        response = self.api_session.get("/@search", params=query)
        self.assertEqual(["/plone/folder/doc"], result_paths(response.json()))

    def test_respect_access_inactive_permission(self):
        # admin can see everything
        response = self.api_session.get("/@search", params={}).json()
        if HAS_PLONE_6:
            # Since Plone 6 the Plone site is indexed ...
            self.assertEqual(response["items_total"], 7)
        else:
            # ... before it was not
            self.assertEqual(response["items_total"], 6)
        response = self.api_session.get(
            "/@search", params={"Title": "Lorem Ipsum"}
        ).json()
        self.assertEqual(response["items_total"], 1)

        # not admin users can't see expired items
        self.api_session.auth = ("editoruser", "secret")

        response = self.api_session.get("/@search", params={}).json()
        if HAS_PLONE_6:
            # Since Plone 6 the Plone site is indexed ...
            self.assertEqual(response["items_total"], 4)
        else:
            # ... before it was not
            self.assertEqual(response["items_total"], 3)
        response = self.api_session.get(
            "/@search", params={"Title": "Lorem Ipsum"}
        ).json()
        self.assertEqual(response["items_total"], 0)

        # now grant permission to Editor to access inactive content
        self.portal.manage_permission(
            "Access inactive portal content", roles=["Manager", "Editor"]
        )
        transaction.commit()

        #  portal-enabled Editor can see expired contents
        response = self.api_session.get("/@search", params={}).json()
        if HAS_PLONE_6:
            # Since Plone 6 the Plone site is indexed ...
            self.assertEqual(response["items_total"], 7)
        else:
            # ... before it was not
            self.assertEqual(response["items_total"], 6)
        response = self.api_session.get(
            "/@search", params={"Title": "Lorem Ipsum"}
        ).json()
        self.assertEqual(response["items_total"], 1)

        # local-enabled Editor can only access expired contents inside folder
        self.api_session.auth = ("localeditor", "secret")
        response = self.api_session.get("/@search", params={}).json()
        if HAS_PLONE_6:
            # Since Plone 6 the Plone site is indexed ...
            self.assertEqual(response["items_total"], 2)
        else:
            # ... before it was not
            self.assertEqual(response["items_total"], 1)
        response = self.api_session.get(
            "/@search", params={"path": "/plone/folder"}
        ).json()

        self.assertEqual(response["items_total"], 3)
        response = self.api_session.get(
            "/@search", params={"Title": "Lorem Ipsum"}
        ).json()
        self.assertEqual(response["items_total"], 0)
        response = self.api_session.get(
            "/@search",
            params={"Title": "Lorem Ipsum", "path": "/plone/folder"},
        ).json()
        self.assertEqual(response["items_total"], 1)

    def test_search_use_site_search_settings_for_types(self):
        response = self.api_session.get(
            "/@search", params={"use_site_search_settings": 1}
        ).json()
        types = {item["@type"] for item in response["items"]}

        self.assertEqual(set(types), {"Folder", "DXTestDocument"})

        registry = getUtility(IRegistry)
        from Products.CMFPlone.interfaces import ISearchSchema

        search_settings = registry.forInterface(ISearchSchema, prefix="plone")
        old = search_settings.types_not_searched
        search_settings.types_not_searched += ("DXTestDocument",)
        transaction.commit()

        response = self.api_session.get(
            "/@search", params={"use_site_search_settings": 1}
        ).json()
        types = {item["@type"] for item in response["items"]}

        self.assertEqual(set(types), {"Folder"})
        search_settings.types_not_searched = old
        transaction.commit()

    def test_search_use_site_search_settings_for_default_sort_order(self):
        response = self.api_session.get(
            "/@search", params={"use_site_search_settings": 1}
        ).json()
        titles = [
            "Some Folder",
            "Lorem Ipsum",
            "Other Document",
            "Another Folder",
            "Document in second folder",
            "Doc outside folder",
        ]
        self.assertEqual([item["title"] for item in response["items"]], titles)

        response = self.api_session.get(
            "/@search", params={"use_site_search_settings": 1, "sort_on": "effective"}
        ).json()
        self.assertEqual(
            [item["title"] for item in response["items"]][0],
            "Other Document",
        )

    def test_search_use_site_search_settings_with_navigation_root(self):

        alsoProvides(self.folder, INavigationRoot)
        transaction.commit()

        response = self.api_session.get(
            "/folder/@search", params={"use_site_search_settings": 1}
        ).json()
        titles = ["Some Folder", "Lorem Ipsum", "Other Document"]
        self.assertEqual([item["title"] for item in response["items"]], titles)

        noLongerProvides(self.folder, INavigationRoot)
        transaction.commit()

    def test_search_use_site_search_settings_with_navigation_root_and_vhm(self):

        if "virtual_hosting" not in self.app.objectIds():
            # If ZopeLite was imported, we have no default virtual
            # host monster
            from Products.SiteAccess.VirtualHostMonster import (
                manage_addVirtualHostMonster,
            )

            manage_addVirtualHostMonster(self.app, "virtual_hosting")
        alsoProvides(self.folder, INavigationRoot)
        transaction.commit()

        vhm_url = "{}/VirtualHostBase/http/plone.org/plone/VirtualHostRoot/{}".format(
            self.app.absolute_url(),
            "/folder/@search",
        )
        response = self.api_session.get(
            vhm_url, params={"use_site_search_settings": 1, "path": "/folder"}
        ).json()
        titles = ["Some Folder", "Lorem Ipsum", "Other Document"]
        self.assertEqual([item["title"] for item in response["items"]], titles)

        noLongerProvides(self.folder, INavigationRoot)
        transaction.commit()

    def test_search_use_site_search_settings_with_vhm(self):

        if "virtual_hosting" not in self.app.objectIds():
            # If ZopeLite was imported, we have no default virtual
            # host monster
            from Products.SiteAccess.VirtualHostMonster import (
                manage_addVirtualHostMonster,
            )

            manage_addVirtualHostMonster(self.app, "virtual_hosting")
        transaction.commit()

        vhm_url = "{}/VirtualHostBase/http/plone.org/plone/VirtualHostRoot/{}".format(
            self.app.absolute_url(),
            "/@search",
        )
        response = self.api_session.get(
            vhm_url, params={"use_site_search_settings": 1, "path": "/"}
        ).json()
        titles = sorted(
            [
                "Another Folder",
                "Doc outside folder",
                "Document in second folder",
                "Lorem Ipsum",
                "Other Document",
                "Some Folder",
            ]
        )
        self.assertEqual(sorted([item["title"] for item in response["items"]]), titles)

        noLongerProvides(self.folder, INavigationRoot)
        transaction.commit()
