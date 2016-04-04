# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

import unittest


class TestCatalogSerializers(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
        self.catalog = getToolByName(self.portal, 'portal_catalog')

        # /plone/my-folder
        self.folder = createContentInContainer(
            self.portal, u'Folder',
            title=u'My Folder')

        # /plone/my-folder/my-document
        self.doc = createContentInContainer(
            self.folder, u'Document',
            created=DateTime(2015, 12, 31, 23, 45),
            title=u'My Document')

    def test_lazy_cat_serialization_empty_resultset(self):
        # Force an empty resultset (Products.ZCatalog.Lazy.LazyCat)
        lazy_cat = self.catalog(path='doesnt-exist')
        results = getMultiAdapter((lazy_cat, self.request), ISerializeToJson)()

        self.assertDictEqual(
            {'member': [], 'items_count': 0},
            results)

    def test_lazy_map_serialization(self):
        lazy_map = self.catalog()
        results = getMultiAdapter((lazy_map, self.request), ISerializeToJson)()
        self.assertEqual(3, len(results['member']))
        self.assertDictContainsSubset(
            {'items_count': 3},
            results)

    def test_brain_summary_representation(self):
        lazy_map = self.catalog()
        results = getMultiAdapter((lazy_map, self.request), ISerializeToJson)()
        self.assertIn(
            {'@id': 'http://nohost/plone/my-folder/my-document',
             'title': 'My Document',
             'description': ''},
            results['member'])
