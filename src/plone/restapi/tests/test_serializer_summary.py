from datetime import datetime
from datetime import timedelta
from DateTime import DateTime
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.app.event.dx.traverser import OccurrenceTraverser
from plone.app.testing import popGlobalRegistry
from plone.app.testing import pushGlobalRegistry
from plone.dexterity.utils import createContentInContainer
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventRecurrence
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.testing import register_static_uuid_utility
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import alsoProvides

import Missing
import pytz
import unittest


try:
    from plone.app.event.adapters import OccurrenceContentListingObject
except ImportError:
    OccurrenceContentListingObject = None


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
            "DXTestDocument",
            id="doc1",
            title="Lorem Ipsum",
            description="Description",
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
                "type_title": "Plone Site",
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
                "type_title": "DX Test Document",
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
                "type_title": "DX Test Document",
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
                "type_title": "DX Test Document",
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
                "type_title": "DX Test Document",
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
            summary["mime_type"] = "text/plain"

        self.maxDiff = None
        self.assertLessEqual(
            {
                "@id": "http://nohost/plone/doc1",
                "@type": "DXTestDocument",
                "CreationDate": "2016-01-21T01:14:48+00:00",
                "Creator": "test_user_1_",
                "Date": "2017-01-21T01:14:48+00:00",
                "Description": "Description",
                "EffectiveDate": "None",
                "ExpirationDate": "None",
                "ModificationDate": "2017-01-21T01:14:48+00:00",
                "Subject": [],
                "Title": "Lorem Ipsum",
                "Type": "DX Test Document",
                "UID": "c6dcbd55ab2746e199cd4ed458000001",
                "author_name": None,
                "cmf_uid": None,
                "commentators": [],
                "created": "2016-01-21T01:14:48+00:00",
                "description": "Description",
                "effective": "1969-12-31T00:00:00+00:00",
                "end": None,
                "exclude_from_nav": False,
                "expires": "2499-12-31T00:00:00+00:00",
                "getIcon": None,
                "getId": "doc1",
                "getObjSize": "0 KB",
                "getPath": "/plone/doc1",
                "getRemoteUrl": None,
                "getURL": "http://nohost/plone/doc1",
                "id": "doc1",
                "in_response_to": None,
                "is_folderish": False,
                "last_comment_date": None,
                "listCreators": ["test_user_1_"],
                "location": None,
                "mime_type": "text/plain",
                "modified": "2017-01-21T01:14:48+00:00",
                "portal_type": "DXTestDocument",
                "review_state": "private",
                "start": None,
                "sync_uid": None,
                "title": "Lorem Ipsum",
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
                "type_title": "DX Test Document",
                "description": "Description",
                "review_state": "private",
            },
            summary,
        )


class TestSummarySerializerswithRecurrenceObjects(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        pushGlobalRegistry(getSite())
        register_static_uuid_utility(prefix="c6dcbd55ab2746e199cd4ed458")

        behaviors = self.portal.portal_types.DXTestDocument.behaviors
        behaviors = behaviors + (
            "plone.eventbasic",
            "plone.eventrecurrence",
        )
        self.portal.portal_types.DXTestDocument.behaviors = behaviors

        self.start = datetime(1995, 7, 31, 13, 45, tzinfo=pytz.timezone("UTC"))
        self.event = createContentInContainer(
            self.portal,
            "DXTestDocument",
            id="doc1",
            title="Lorem Ipsum event",
            description="Description event",
            start=self.start,
            end=self.start + timedelta(hours=1),
            recurrence="RRULE:FREQ=DAILY;COUNT=3",  # see https://github.com/plone/plone.app.event/blob/master/plone/app/event/tests/base_setup.py
        )

        alsoProvides(self.event, IEvent)
        alsoProvides(self.event, IEventRecurrence)

    def tearDown(self):
        popGlobalRegistry(getSite())

    @unittest.skipIf(
        OccurrenceContentListingObject is not None,
        "this test needs a plone.app.event version that does not include a IContentListingObject adapter",
    )
    def test_dx_event_with_recurrence_old_version(self):
        tomorrow = self.start + timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        traverser = OccurrenceTraverser(self.event, self.request)
        occurrence = traverser.publishTraverse(self.request, tomorrow_str)

        with self.assertRaises(TypeError):
            getMultiAdapter((occurrence, self.request), ISerializeToJsonSummary)()

    @unittest.skipIf(
        OccurrenceContentListingObject is None,
        "this test needs a plone.app.event version that includes a IContentListingObject adapter",
    )
    def test_dx_event_with_recurrence_new_version(self):
        tomorrow = self.start + timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        traverser = OccurrenceTraverser(self.event, self.request)
        occurrence = traverser.publishTraverse(self.request, tomorrow_str)
        self.request.form["metadata_fields"] = ["start"]
        summary = getMultiAdapter((occurrence, self.request), ISerializeToJsonSummary)()
        self.assertEqual(
            datetime.fromisoformat(summary["start"]).date().isoformat(),
            tomorrow.date().isoformat(),
        )
        self.assertEqual(summary["title"], occurrence.Title())
