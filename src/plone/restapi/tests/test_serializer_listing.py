# -*- coding: utf-8 -*-
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import IContentListingObjectSerializer
from plone.restapi.interfaces import IContentListingSerializer
from plone.restapi.serializer.listing import ContentListingObjectSerializer
from plone.restapi.serializer.listing import ContentListingSerializer
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass


class TestContentListingSerialization(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST

        self.folder = createContentInContainer(
            self.portal, u'Folder',
            title=u'Folder',
        )

        self.doc1 = createContentInContainer(
            self.folder, u'Document',
            title=u'Document 1',
            description=u'Foo',
        )

        self.doc2 = createContentInContainer(
            self.folder, u'Document',
            title=u'Document 2',
            description=u'Bar',
        )

    def test_content_listing_serialization(self):
        listing = getMultiAdapter(
            (IContentListing(self.folder.objectValues()), self.request),
            IContentListingSerializer)()

        self.assertEquals([
            {'@id': 'http://nohost/plone/folder/document-1',
             'title': 'Document 1',
             'description': 'Foo'},
            {'@id': 'http://nohost/plone/folder/document-2',
             'title': 'Document 2',
             'description': 'Bar'}],
            listing)

    def test_content_listing_object_serialization(self):
        entry = getMultiAdapter(
            (IContentListingObject(self.doc1), self.request),
            IContentListingObjectSerializer)()

        self.assertEquals(
            {'@id': 'http://nohost/plone/folder/document-1',
             'title': 'Document 1',
             'description': 'Foo'},
            entry)

    def test_content_listing_serializer_implements_iface(self):
        verifyClass(
            IContentListingSerializer, ContentListingSerializer)

    def test_content_listing_object_serializer_implements_iface(self):
        verifyClass(
            IContentListingObjectSerializer, ContentListingObjectSerializer)
