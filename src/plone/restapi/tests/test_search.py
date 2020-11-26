# -*- coding: utf-8 -*-
from datetime import date
from DateTime import DateTime
from plone import api
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from plone.restapi import HAS_AT
from plone.restapi.testing import PLONE_RESTAPI_AT_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.restapi.tests.helpers import result_paths
from plone.uuid.interfaces import IMutableUUID
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

import six
import transaction
import unittest


class TestSearchFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST
        self.catalog = getToolByName(self.portal, "portal_catalog")

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        # /plone/folder
        self.folder = createContentInContainer(
            self.portal, u"Folder", id=u"folder", title=u"Some Folder"
        )

        # /plone/folder/doc
        self.doc = createContentInContainer(
            self.folder,
            u"DXTestDocument",
            id="doc",
            title=u"Lorem Ipsum",
            start=DateTime(1950, 1, 1, 0, 0),
            effective=DateTime(1995, 1, 1, 0, 0),
            expires=DateTime(1999, 1, 1, 0, 0),
            test_int_field=42,
            test_list_field=["Keyword1", "Keyword2", "Keyword3"],
            test_bool_field=True,
            test_richtext_field=RichTextValue(
                raw=u"<p>Some Text</p>",
                mimeType="text/html",
                outputMimeType="text/html",
            ),
        )
        IMutableUUID(self.doc).set("77779ffa110e45afb1ba502f75f77777")
        self.doc.reindexObject()

        # /plone/folder/other-document
        self.doc2 = createContentInContainer(
            self.folder,
            u"DXTestDocument",
            id="other-document",
            title=u"Other Document",
            description=u"\xdcbersicht",
            start=DateTime(1975, 1, 1, 0, 0),
            effective=DateTime(2015, 1, 1, 0, 0),
            expires=DateTime(2020, 1, 1, 0, 0),
            test_list_field=["Keyword2", "Keyword3"],
            test_bool_field=False,
        )

        # /plone/folder2
        self.folder2 = createContentInContainer(
            self.portal, u"Folder", id=u"folder2", title=u"Another Folder"
        )

        # /plone/folder2/doc
        createContentInContainer(
            self.folder2,
            u"DXTestDocument",
            id="doc",
            title=u"Document in second folder",
            start=DateTime(1975, 1, 1, 0, 0),
            effective=DateTime(2015, 1, 1, 0, 0),
            expires=DateTime(2020, 1, 1, 0, 0),
            test_bool_field=False,
        )

        # /plone/doc-outside-folder
        createContentInContainer(
            self.portal,
            u"DXTestDocument",
            id="doc-outside-folder",
            title=u"Doc outside folder",
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
            results[u"items_total"],
            len(results[u"items"]),
            "items_total property should match actual item count.",
        )

    def test_search_on_context_constrains_query_by_path(self):
        response = self.api_session.get("/folder/@search")
        self.assertSetEqual(
            {u"/plone/folder", u"/plone/folder/doc", u"/plone/folder/other-document"},
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
        vhm_url = "%s/VirtualHostBase/http/plone.org/plone/VirtualHostRoot/%s" % (
            self.app.absolute_url(),
            "@search?path=/folder",
        )
        response = self.api_session.get(vhm_url)
        self.assertSetEqual(
            {u"/folder", u"/folder/doc", u"/folder/other-document"},
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
        vhm_url = "%s/VirtualHostBase/http/plone.org/plone/VirtualHostRoot/%s" % (
            self.app.absolute_url(),
            "@search",
        )
        response = self.api_session.get(vhm_url, params=query)
        self.assertSetEqual(
            {
                u"/folder",
                u"/folder/doc",
                u"/folder/other-document",
                u"/folder2",
                u"/folder2/doc",
            },
            set(result_paths(response.json())),
        )

        # path as a dict with a query list
        query = {"path.query": ["/folder", "/folder2"]}

        # If we go through the VHM we will get results for multiple paths
        # if we only use the part of the path inside the VHM
        vhm_url = "%s/VirtualHostBase/http/plone.org/plone/VirtualHostRoot/%s" % (
            self.app.absolute_url(),
            "@search",
        )
        response = self.api_session.get(vhm_url, params=query)
        self.assertSetEqual(
            {
                u"/folder",
                u"/folder/doc",
                u"/folder/other-document",
                u"/folder2",
                u"/folder2/doc",
            },
            set(result_paths(response.json())),
        )

    def test_path_gets_prefilled_if_missing_from_path_query_dict(self):
        response = self.api_session.get("/@search?path.depth=1")
        self.assertSetEqual(
            {u"/plone/folder", u"/plone/folder2", u"/plone/doc-outside-folder"},
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
                u"@id": self.portal_url + u"/folder/doc",
                u"title": u"Lorem Ipsum",
                u"portal_type": u"DXTestDocument",
                u"review_state": u"private",
            },
            response.json()["items"][0],
        )

    def test_full_metadata_retrieval(self):
        query = {"SearchableText": "lorem", "metadata_fields": "_all"}
        response = self.api_session.get("/@search", params=query)

        first_item = response.json()["items"][0]
        self.assertLessEqual(
            {
                u"@id": self.portal_url + u"/folder/doc",
                u"Creator": u"test_user_1_",
                u"Description": u"",
                u"EffectiveDate": u"None",
                u"ExpirationDate": u"None",
                u"Subject": [],
                u"Title": u"Lorem Ipsum",
                u"Type": u"DX Test Document",
                u"UID": u"77779ffa110e45afb1ba502f75f77777",
                u"author_name": None,
                u"cmf_uid": None,
                u"commentators": [],
                u"description": u"",
                u"effective": u"1995-01-01T00:00:00+00:00",
                u"end": None,
                u"exclude_from_nav": False,
                u"expires": u"1999-01-01T00:00:00+00:00",
                u"getId": u"doc",
                u"getPath": u"/plone/folder/doc",
                u"getRemoteUrl": None,
                u"getURL": self.portal_url + u"/folder/doc",
                u"id": u"doc",
                u"in_response_to": None,
                u"is_folderish": False,
                u"last_comment_date": None,
                u"listCreators": [u"test_user_1_"],
                u"location": None,
                u"portal_type": u"DXTestDocument",
                u"review_state": u"private",
                u"start": u"1950-01-01T00:00:00+00:00",
                u"sync_uid": None,
                u"title": u"Lorem Ipsum",
                u"total_comments": 0,
            }.items(),
            first_item.items(),
        )
        # This value changed in Plone 5.2
        # (Dexterity gained support for getObjSize)
        self.assertIn(first_item[u"getObjSize"], (u"0 KB", u"1 KB"))

    def test_full_objects_retrieval(self):
        query = {
            "SearchableText": "lorem",
            "metadata_fields": ["portal_type", "review_state"],
            "fullobjects": True,
        }
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(
            u"<p>Some Text</p>",
            response.json()["items"][0]["test_richtext_field"]["data"],
        )
        self.assertEqual(
            self.portal_url + u"/folder/doc", response.json()["items"][0]["@id"]
        )

    def test_full_objects_retrieval_discussion(self):
        # Allow discussion
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        self.doc.allow_discussion = True

        transaction.commit()

        url = "{}/@comments".format(self.doc.absolute_url())
        self.api_session.post(url, json={"text": "comment 1"})
        transaction.commit()

        query = {"portal_type": "Discussion Item", "fullobjects": True}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_full_objects_retrieval_collections(self):
        self.collection = createContentInContainer(
            self.folder, u"Collection", id="collection"
        )
        transaction.commit()

        query = {"portal_type": "Collection", "fullobjects": True}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    # ZCTextIndex

    def test_fulltext_search(self):
        query = {"SearchableText": "lorem"}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual([u"/plone/folder/doc"], result_paths(response.json()))

    def test_fulltext_search_with_non_ascii_characters(self):
        query = {"SearchableText": u"\xfcbersicht"}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(
            [u"/plone/folder/other-document"], result_paths(response.json())
        )

    # KeywordIndex

    def test_keyword_index_str_query(self):
        query = {"test_list_field": "Keyword1"}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual([u"/plone/folder/doc"], result_paths(response.json()))

    def test_keyword_index_str_query_or(self):
        query = {"test_list_field": ["Keyword2", "Keyword3"]}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(
            [u"/plone/folder/doc", u"/plone/folder/other-document"],
            result_paths(response.json()),
        )

    def test_keyword_index_str_query_and(self):
        query = {
            "test_list_field.query": ["Keyword1", "Keyword2"],
            "test_list_field.operator": "and",
        }
        response = self.api_session.get("/@search", params=query)

        self.assertEqual([u"/plone/folder/doc"], result_paths(response.json()))

    @unittest.skipIf(six.PY3, "Python 3 can't sort mixed types")
    def test_keyword_index_int_query(self):
        self.doc.test_list_field = [42, 23]
        self.doc.reindexObject()
        transaction.commit()

        query = {"test_list_field:int": 42}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual([u"/plone/folder/doc"], result_paths(response.json()))

    # BooleanIndex

    def test_boolean_index_query(self):
        query = {"test_bool_field": True, "portal_type": "DXTestDocument"}
        response = self.api_session.get("/folder/@search", params=query)
        self.assertEqual([u"/plone/folder/doc"], result_paths(response.json()))

        query = {"test_bool_field": False, "portal_type": "DXTestDocument"}
        response = self.api_session.get("/folder/@search", params=query)
        self.assertEqual(
            [u"/plone/folder/other-document"], result_paths(response.json())
        )

    # FieldIndex

    def test_field_index_int_query(self):
        query = {"test_int_field:int": 42}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual([u"/plone/folder/doc"], result_paths(response.json()))

    def test_field_index_int_range_query(self):
        query = {
            "test_int_field.query:int": [41, 43],
            "test_int_field.range": "min:max",
        }
        response = self.api_session.get("/@search", params=query)

        self.assertEqual([u"/plone/folder/doc"], result_paths(response.json()))

    # ExtendedPathIndex

    def test_extended_path_index_query(self):
        query = {"path": "/".join(self.folder.getPhysicalPath())}

        response = self.api_session.get("/@search", params=query)

        self.assertEqual(
            sorted(
                [
                    u"/plone/folder",
                    u"/plone/folder/doc",
                    u"/plone/folder/other-document",
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
                    u"/plone/folder",
                    u"/plone/folder/doc",
                    u"/plone/folder/other-document",
                    u"/plone/folder2",
                    u"/plone/folder2/doc",
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
                    u"/plone/folder",
                    u"/plone/folder/doc",
                    u"/plone/folder/other-document",
                    u"/plone/folder2",
                    u"/plone/folder2/doc",
                ]
            ),
            sorted(result_paths(response.json())),
        )

    def test_extended_path_index_depth_limiting(self):
        lvl1 = createContentInContainer(self.portal, u"Folder", id=u"lvl1")
        lvl2 = createContentInContainer(lvl1, u"Folder", id=u"lvl2")
        createContentInContainer(lvl2, u"Folder", id=u"lvl3")
        transaction.commit()

        path = "/plone/lvl1"

        # Depth 0 - only object identified by path
        query = {"path.query": path, "path.depth": 0}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual([u"/plone/lvl1"], result_paths(response.json()))

        # Depth 1 - immediate children
        query = {"path.query": path, "path.depth": 1}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual([u"/plone/lvl1/lvl2"], result_paths(response.json()))

        # No depth - object itself and all children
        query = {"path": path}
        response = self.api_session.get("/@search", params=query)

        self.assertSetEqual(
            {u"/plone/lvl1", u"/plone/lvl1/lvl2", u"/plone/lvl1/lvl2/lvl3"},
            set(result_paths(response.json())),
        )

    # DateIndex

    def test_date_index_query(self):
        query = {"start": date(1950, 1, 1).isoformat()}
        response = self.api_session.get("/@search", params=query)

        self.assertEqual([u"/plone/folder/doc"], result_paths(response.json()))

    def test_date_index_ranged_query(self):
        query = {
            "start.query": [date(1949, 1, 1).isoformat(), date(1951, 1, 1).isoformat()],
            "start.range": "min:max",
        }
        response = self.api_session.get("/@search", params=query)

        self.assertEqual([u"/plone/folder/doc"], result_paths(response.json()))

    # DateRangeIndex

    def test_date_range_index_query(self):
        query = {"effectiveRange": date(1997, 1, 1).isoformat()}
        response = self.api_session.get("/folder/@search", params=query)

        self.assertEqual(2, len(result_paths(response.json())))
        self.assertTrue(u"/plone/folder" in result_paths(response.json()))
        self.assertTrue(u"/plone/folder/doc" in result_paths(response.json()))

    # DateRecurringIndex

    def test_date_recurring_index_query(self):
        from datetime import datetime

        createContentInContainer(
            self.folder,
            u"Event",
            id=u"event",
            title=u"Event",
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

        self.assertEqual([u"/plone/folder/event"], result_paths(response.json()))

        # No event that day
        query = {"start": date(2013, 1, 2).isoformat()}
        response = self.api_session.get("/folder/@search", params=query)

        self.assertEqual([], result_paths(response.json()))

        # Second occurrence
        query = {"start": date(2013, 1, 3).isoformat()}
        response = self.api_session.get("/folder/@search", params=query)

        self.assertEqual([u"/plone/folder/event"], result_paths(response.json()))

        # Ranged query
        query = {
            "start.query": [date(2013, 1, 1).isoformat(), date(2013, 1, 5).isoformat()],
            "start.range": "min:max",
        }
        response = self.api_session.get("/folder/@search", params=query)

        self.assertEqual([u"/plone/folder/event"], result_paths(response.json()))

    # UUIDIndex

    def test_uuid_index_query(self):
        IMutableUUID(self.doc).set("7777a074cb4240d08c9a129e3a837777")
        self.doc.reindexObject()
        transaction.commit()

        query = {"UID": "7777a074cb4240d08c9a129e3a837777"}
        response = self.api_session.get("/@search", params=query)
        self.assertEqual([u"/plone/folder/doc"], result_paths(response.json()))


class TestSearchATFunctional(unittest.TestCase):
    layer = PLONE_RESTAPI_AT_FUNCTIONAL_TESTING

    def setUp(self):
        if not HAS_AT:
            raise unittest.SkipTest("Skip tests if Archetypes is not present")
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST
        self.catalog = getToolByName(self.portal, "portal_catalog")

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        # /plone/folder
        with api.env.adopt_roles(["Manager"]):
            self.folder = api.content.create(
                type=u"ATTestFolder",
                id=u"folder",
                title=u"Some Folder",
                container=self.portal,
            )

            # /plone/folder/doc
            self.doc = api.content.create(
                container=self.folder,
                type=u"ATTestDocument",
                id="doc",
                title=u"Lorem Ipsum",
                start=DateTime(1950, 1, 1, 0, 0),
                effective=DateTime(1995, 1, 1, 0, 0),
                expires=DateTime(1999, 1, 1, 0, 0),
                testIntegerField=42,
                testLinesField=["Keyword1", "Keyword2", "Keyword3"],
                testBooleanField=True,
                testTextField=u"<p>Some Text</p>",
            )

            # /plone/folder/other-document
            self.doc2 = api.content.create(
                container=self.folder,
                type=u"ATTestDocument",
                id="other-document",
                title=u"Other Document",
                description=u"\xdcbersicht",
                start=DateTime(1975, 1, 1, 0, 0),
                effective=DateTime(2015, 1, 1, 0, 0),
                expires=DateTime(2020, 1, 1, 0, 0),
                testLinesField=["Keyword2", "Keyword3"],
                testBooleanField=False,
            )

            # /plone/doc-outside-folder
            api.content.create(
                container=self.portal,
                type=u"ATTestDocument",
                id="doc-outside-folder",
                title=u"Doc outside folder",
            )

        transaction.commit()

    def test_full_objects_retrieval(self):
        query = {
            "SearchableText": "lorem",
            "metadata_fields": ["portal_type", "review_state"],
            "fullobjects": True,
        }
        response = self.api_session.get("/@search", params=query)

        self.assertEqual(
            {u"data": u" Some Text ", u"content-type": u"text/plain"},
            response.json()["items"][0]["testTextField"],
        )
        self.assertEqual(
            self.portal_url + u"/folder/doc", response.json()["items"][0]["@id"]
        )
