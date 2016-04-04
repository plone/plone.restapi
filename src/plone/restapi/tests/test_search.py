# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.restapi.tests.helpers import result_paths
from Products.CMFCore.utils import getToolByName

import transaction
import unittest


class TestSearchFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST
        self.catalog = getToolByName(self.portal, 'portal_catalog')

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        # /plone/folder
        self.folder = createContentInContainer(
            self.portal, u'Folder',
            id=u'folder',
            title=u'Some Folder')

        # /plone/folder/doc
        self.doc = createContentInContainer(
            self.folder, u'DXTestDocument',
            id='doc',
            title=u'Lorem Ipsum',
        )

        # /plone/folder/other-document
        self.doc2 = createContentInContainer(
            self.folder, u'DXTestDocument',
            id='other-document',
            title=u'Other Document',
            description=u'\xdcbersicht',
        )

        # /plone/doc-outside-folder
        createContentInContainer(
            self.portal, u'DXTestDocument',
            id='doc-outside-folder',
            title=u'Doc outside folder',
        )

        transaction.commit()

    def test_overall_response_format(self):
        response = self.api_session.get('/search')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get('Content-Type'),
            'application/json',
        )

        results = response.json()
        self.assertEqual(
            results[u'items_count'],
            len(results[u'member']),
            'items_count property should match actual item count.'
        )

    def test_search_on_context_constrains_query_by_path(self):
        response = self.api_session.get('/folder/search')

        self.assertSetEqual(
            {u'/plone/folder',
             u'/plone/folder/doc',
             u'/plone/folder/other-document'},
            set(result_paths(response.json())))

    def test_fulltext_search(self):
        query = {'SearchableText': 'lorem'}
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/folder/doc'],
            result_paths(response.json())
        )

    def test_fulltext_search_with_non_ascii_characters(self):
        query = {'SearchableText': u'\xfcbersicht'}
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/folder/other-document'],
            result_paths(response.json())
        )
