# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.app.testing import popGlobalRegistry
from plone.app.testing import pushGlobalRegistry
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi import HAS_AT
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.testing import PLONE_RESTAPI_AT_INTEGRATION_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.testing import register_static_uuid_utility
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component.hooks import getSite

import Missing
import unittest


class TestSummarySerializers(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        pushGlobalRegistry(getSite())
        register_static_uuid_utility(prefix="c6dcbd55ab2746e199cd4ed458")

        self.catalog = getToolByName(self.portal, "portal_catalog")

        self.doc1 = createContentInContainer(
            self.portal,
            u"DXTestDocument",
            id=u"doc1",
            title=u"Lorem Ipsum",
            description=u"Description",
        )

        self.doc1.creation_date = DateTime("2016-01-21T01:14:48+00:00")
        self.doc1.modification_date = DateTime("2017-01-21T01:14:48+00:00")
        self.doc1.reindexObject(["modified"])

    def tearDown(self):
        popGlobalRegistry(getSite())

    def test_site_root_summary(self):
        summary = getMultiAdapter(
            (self.portal, self.request), ISerializeToJsonSummary
        )()

        self.assertDictEqual(
            {
                "@id": "http://nohost/plone",
                "@type": "Plone Site",
                "title": "Plone site",
                "description": "",
            },
            summary,
        )

    def test_brain_summary(self):
        brain = self.catalog(UID=self.doc1.UID())[0]
        summary = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()

        self.assertDictEqual(
            {
                "@id": "http://nohost/plone/doc1",
                "@type": "DXTestDocument",
                "title": "Lorem Ipsum",
                "description": "Description",
                "review_state": "private",
            },
            summary,
        )

        # Must also work if we're dealing with a CatalogContentListingObject
        # (because the brain has already been adapted to IContentListingObject,
        # as is the case for collection results)
        listing_obj = IContentListingObject(brain)
        summary = getMultiAdapter(
            (listing_obj, self.request), ISerializeToJsonSummary
        )()

        self.assertDictEqual(
            {
                "@id": "http://nohost/plone/doc1",
                "@type": "DXTestDocument",
                "title": "Lorem Ipsum",
                "description": "Description",
                "review_state": "private",
            },
            summary,
        )

    def test_brain_summary_with_missing_value(self):
        brain = self.catalog(UID=self.doc1.UID())[0]
        brain.Description = Missing.Value

        summary = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()

        self.assertDictEqual(
            {
                "@id": "http://nohost/plone/doc1",
                "@type": "DXTestDocument",
                "title": "Lorem Ipsum",
                "description": None,
                "review_state": "private",
            },
            summary,
        )

    def test_brain_summary_includes_additional_metadata_fields(self):
        brain = self.catalog(UID=self.doc1.UID())[0]
        self.request.form.update({"metadata_fields": ["UID", "Creator"]})
        summary = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()

        self.assertDictEqual(
            {
                "@id": "http://nohost/plone/doc1",
                "@type": "DXTestDocument",
                "UID": "c6dcbd55ab2746e199cd4ed458000001",
                "Creator": "test_user_1_",
                "title": "Lorem Ipsum",
                "description": "Description",
                "review_state": "private",
            },
            summary,
        )

    def test_brain_summary_includes_all_metadata_fields(self):
        brain = self.catalog(UID=self.doc1.UID())[0]
        self.request.form.update({"metadata_fields": "_all"})
        summary = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()

        # mime_type was added in Plone 5.1
        # Make sure tests pass on older Plone versions
        if "mime_type" not in summary:
            summary["mime_type"] = u"text/plain"

        self.maxDiff = None
        self.assertLessEqual(
            {
                "@id": u"http://nohost/plone/doc1",
                "@type": u"DXTestDocument",
                "CreationDate": u"2016-01-21T01:14:48+00:00",
                "Creator": u"test_user_1_",
                "Date": u"2017-01-21T01:14:48+00:00",
                "Description": u"Description",
                "EffectiveDate": u"None",
                "ExpirationDate": u"None",
                "ModificationDate": u"2017-01-21T01:14:48+00:00",
                "Subject": [],
                "Title": u"Lorem Ipsum",
                "Type": u"DX Test Document",
                "UID": u"c6dcbd55ab2746e199cd4ed458000001",
                "author_name": None,
                "cmf_uid": None,
                "commentators": [],
                "created": u"2016-01-21T01:14:48+00:00",
                "description": u"Description",
                "effective": u"1969-12-31T00:00:00+00:00",
                "end": None,
                "exclude_from_nav": False,
                "expires": u"2499-12-31T00:00:00+00:00",
                "getIcon": None,
                "getId": u"doc1",
                "getObjSize": u"0 KB",
                "getPath": u"/plone/doc1",
                "getRemoteUrl": None,
                "getURL": u"http://nohost/plone/doc1",
                "id": u"doc1",
                "in_response_to": None,
                "is_folderish": False,
                "last_comment_date": None,
                "listCreators": [u"test_user_1_"],
                "location": None,
                "mime_type": u"text/plain",
                "modified": u"2017-01-21T01:14:48+00:00",
                "portal_type": u"DXTestDocument",
                "review_state": u"private",
                "start": None,
                "sync_uid": None,
                "title": u"Lorem Ipsum",
                "total_comments": 0,
            }.items(),
            summary.items(),
        )

    def test_dx_type_summary(self):
        summary = getMultiAdapter((self.doc1, self.request), ISerializeToJsonSummary)()

        self.assertDictEqual(
            {
                "@id": "http://nohost/plone/doc1",
                "@type": "DXTestDocument",
                "title": "Lorem Ipsum",
                "description": "Description",
                "review_state": "private",
            },
            summary,
        )


class TestSummarySerializersATTypes(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        if not HAS_AT:
            raise unittest.SkipTest("Skip tests if Archetypes is not present")
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])

        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "ATTestDocument",
                id="doc1",
                title="Lorem Ipsum",
                description="Description",
            )
        ]

    def test_at_type_summary(self):
        summary = getMultiAdapter((self.doc1, self.request), ISerializeToJsonSummary)()

        self.assertDictEqual(
            {
                "@id": "http://nohost/plone/doc1",
                "@type": "ATTestDocument",
                "title": "Lorem Ipsum",
                "description": "Description",
                "review_state": "private",
            },
            summary,
        )
