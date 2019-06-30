# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from plone.dexterity.utils import createContentInContainer
from plone.restapi import HAS_AT
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.testing import PLONE_RESTAPI_AT_INTEGRATION_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.uuid.interfaces import IMutableUUID
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

import unittest


class TestCatalogSerializers(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.portal.REQUEST
        self.catalog = getToolByName(self.portal, "portal_catalog")

        # /plone/my-folder
        self.folder = createContentInContainer(
            self.portal, u"Folder", title=u"My Folder"
        )

        # /plone/my-folder/my-document
        self.doc = createContentInContainer(
            self.folder,
            u"Document",
            creation_date=DateTime(2015, 12, 31, 23, 45),
            title=u"My Document",
        )

        IMutableUUID(self.doc).set("77779ffa110e45afb1ba502f75f77777")
        self.doc.reindexObject()

    def test_lazy_cat_serialization_empty_resultset(self):
        # Force an empty resultset (Products.ZCatalog.Lazy.LazyCat)
        lazy_cat = self.catalog(path="doesnt-exist")
        results = getMultiAdapter((lazy_cat, self.request), ISerializeToJson)()

        self.assertDictEqual(
            {"@id": "http://nohost", "items": [], "items_total": 0}, results
        )

    def test_lazy_map_serialization(self):
        # Test serialization of a Products.ZCatalog.Lazy.LazyMap
        lazy_map = self.catalog()
        results = getMultiAdapter((lazy_map, self.request), ISerializeToJson)()

        self.assertDictContainsSubset({"@id": "http://nohost"}, results)
        self.assertDictContainsSubset({"items_total": 2}, results)
        self.assertEqual(2, len(results["items"]))

    def test_lazy_map_serialization_with_fullobjects(self):
        # Test serialization of a Products.ZCatalog.Lazy.LazyMap
        lazy_map = self.catalog(path="/plone/my-folder/my-document")
        results = getMultiAdapter((lazy_map, self.request), ISerializeToJson)(
            fullobjects=True
        )

        self.assertDictContainsSubset({"@id": "http://nohost"}, results)
        self.assertDictContainsSubset({"items_total": 1}, results)
        self.assertEqual(1, len(results["items"]))
        result_item = results["items"][0]

        self.assertDictContainsSubset(
            {
                "@id": "http://nohost/plone/my-folder/my-document",
                "@type": "Document",
                u"changeNote": u"",
                u"contributors": [],
                u"creators": [u"test_user_1_"],
                u"description": u"",
                u"effective": None,
                u"exclude_from_nav": False,
                u"expires": None,
                "id": u"my-document",
                "is_folderish": False,
                u"language": u"",
                "layout": "document_view",
                "parent": {
                    u"@id": u"http://nohost/plone/my-folder",
                    u"@type": u"Folder",
                    u"description": u"",
                    u"review_state": u"private",
                    u"title": u"My Folder",
                },
                u"relatedItems": [],
                "review_state": "private",
                u"rights": u"",
                u"subjects": [],
                u"table_of_contents": None,
                u"text": None,
                u"title": u"My Document",
                "version": "current",
            },
            result_item,
        )

    def test_brain_summary_representation(self):
        lazy_map = self.catalog(path="/plone/my-folder/my-document")
        brain = lazy_map[0]
        result = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
        self.assertEqual(
            {
                "@id": "http://nohost/plone/my-folder/my-document",
                "@type": "Document",
                "title": "My Document",
                "description": "",
                "review_state": "private",
            },
            result,
        )


class TestCatalogATSerializers(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        if not HAS_AT:
            raise unittest.SkipTest("Skip tests if Archetypes is not present")
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.portal.REQUEST
        self.catalog = getToolByName(self.portal, "portal_catalog")

        with api.env.adopt_roles(["Manager"]):
            # /plone/my-folder
            self.folder = api.content.create(
                container=self.portal, type=u"ATTestFolder", title=u"My Folder"
            )

            # /plone/my-folder/my-document
            self.doc = api.content.create(
                container=self.folder,
                type=u"ATTestDocument",
                testTextField="My content",
                testIntegerField=42,
                title=u"My Document",
            )

    def test_lazy_map_serialization_with_fullobjects(self):
        # Test serialization of a Products.ZCatalog.Lazy.LazyMap
        lazy_map = self.catalog(path="/plone/my-folder/my-document")
        results = getMultiAdapter((lazy_map, self.request), ISerializeToJson)(
            fullobjects=True
        )

        self.assertDictContainsSubset({"@id": "http://nohost"}, results)
        self.assertDictContainsSubset({"items_total": 1}, results)
        self.assertEqual(1, len(results["items"]))
        result_item = results["items"][0]

        self.assertDictContainsSubset(
            {
                "@id": "http://nohost/plone/my-folder/my-document",
                "@type": "ATTestDocument",
                "contributors": [],
                "creators": [u"test_user_1_"],
                "description": {"content-type": u"text/plain", "data": u""},
                "effectiveDate": None,
                "excludeFromNav": False,
                "expirationDate": None,
                "id": u"my-document",
                "is_folderish": False,
                "language": u"en",
                "layout": "base_view",
                "location": u"",
                "parent": {
                    u"@id": u"http://nohost/plone/my-folder",
                    u"@type": u"ATTestFolder",
                    u"description": u"",
                    u"review_state": u"private",
                    u"title": u"My Folder",
                },
                "relatedItems": [],
                "review_state": "private",
                "rights": {"content-type": u"text/plain", "data": u""},
                "subject": [],
                "tableContents": False,
                "testBlobImageField": None,
                "testBooleanField": False,
                "testDateTimeField": None,
                "testFixedPointField": None,
                "testFloatField": None,
                "testImageField": None,
                "testIntegerField": 42,
                "testLinesField": [],
                "testMVReferenceField": [],
                "testQueryField": [],
                "testReadonlyField": u"",
                "testReferenceField": None,
                "testRequiredField": u"",
                "testStringField": u"",
                "testTextField": {"content-type": u"text/plain", "data": u"My content"},
                "testURLField": u"",
                "testWritePermissionField": u"",
                "text": {"content-type": u"text/plain", "data": u""},
                "title": u"My Document",
            },
            result_item,
        )
