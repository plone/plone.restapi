# -*- coding: utf-8 -*-
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.testing import PLONE_RESTAPI_AT_INTEGRATION_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

import Missing
import unittest


class TestSummarySerializers(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.catalog = getToolByName(self.portal, 'portal_catalog')

        self.doc1 = createContentInContainer(
            self.portal, u'DXTestDocument',
            id=u'doc1',
            title=u'Lorem Ipsum',
            description=u'Description')

    def test_site_root_summary(self):
        summary = getMultiAdapter(
            (self.portal, self.request), ISerializeToJsonSummary)()

        self.assertDictEqual(
            {'@id': 'http://nohost/plone',
             '@type': 'Plone Site',
             'title': 'Plone site',
             'description': ''},
            summary)

    def test_brain_summary(self):
        brain = self.catalog(UID=self.doc1.UID())[0]
        summary = getMultiAdapter(
            (brain, self.request), ISerializeToJsonSummary)()

        self.assertDictEqual(
            {'@id': 'http://nohost/plone/doc1',
             '@type': 'DXTestDocument',
             'title': 'Lorem Ipsum',
             'description': 'Description',
             'review_state': 'private'},
            summary)

        # Must also work if we're dealing with a CatalogContentListingObject
        # (because the brain has already been adapted to IContentListingObject,
        # as is the case for collection results)
        listing_obj = IContentListingObject(brain)
        summary = getMultiAdapter(
            (listing_obj, self.request), ISerializeToJsonSummary)()

        self.assertDictEqual(
            {'@id': 'http://nohost/plone/doc1',
             '@type': 'DXTestDocument',
             'title': 'Lorem Ipsum',
             'description': 'Description',
             'review_state': 'private'},
            summary)

    def test_brain_summary_with_missing_value(self):
        brain = self.catalog(UID=self.doc1.UID())[0]
        brain.Description = Missing.Value

        summary = getMultiAdapter(
            (brain, self.request), ISerializeToJsonSummary)()

        self.assertDictEqual(
            {'@id': 'http://nohost/plone/doc1',
             '@type': 'DXTestDocument',
             'title': 'Lorem Ipsum',
             'description': None,
             'review_state': 'private'},
            summary)

    def test_dx_type_summary(self):
        summary = getMultiAdapter(
            (self.doc1, self.request), ISerializeToJsonSummary)()

        self.assertDictEqual(
            {'@id': 'http://nohost/plone/doc1',
             '@type': 'DXTestDocument',
             'title': 'Lorem Ipsum',
             'description': 'Description',
             'review_state': 'private'},
            summary)


class TestSummarySerializersATTypes(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        self.doc1 = self.portal[self.portal.invokeFactory(
            'ATTestDocument',
            id='doc1',
            title='Lorem Ipsum',
            description='Description')]

    def test_at_type_summary(self):
        summary = getMultiAdapter(
            (self.doc1, self.request), ISerializeToJsonSummary)()

        self.assertDictEqual(
            {'@id': 'http://nohost/plone/doc1',
             '@type': 'ATTestDocument',
             'title': 'Lorem Ipsum',
             'description': 'Description',
             'review_state': 'private'},
            summary)
