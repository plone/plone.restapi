# -*- coding: utf-8 -*-
from datetime import date
from DateTime import DateTime
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.restapi.tests.helpers import result_paths
from plone.uuid.interfaces import IMutableUUID
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
            created=DateTime(1950, 1, 1, 0, 0),
            effective=DateTime(1995, 1, 1, 0, 0),
            expires=DateTime(1999, 1, 1, 0, 0),
            test_int_field=42,
            test_list_field=['Keyword1', 'Keyword2', 'Keyword3'],
            test_bool_field=True,
        )

        # /plone/folder/other-document
        self.doc2 = createContentInContainer(
            self.folder, u'DXTestDocument',
            id='other-document',
            title=u'Other Document',
            description=u'\xdcbersicht',
            created=DateTime(1975, 1, 1, 0, 0),
            effective=DateTime(2015, 1, 1, 0, 0),
            expires=DateTime(2020, 1, 1, 0, 0),
            test_list_field=['Keyword2', 'Keyword3'],
            test_bool_field=False,
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

    # ZCTextIndex

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

    # KeywordIndex

    def test_keyword_index_str_query(self):
        query = {'test_list_field': 'Keyword1'}
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/folder/doc'],
            result_paths(response.json())
        )

    def test_keyword_index_str_query_or(self):
        query = {'test_list_field': ['Keyword2', 'Keyword3']}
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/folder/doc',
             u'/plone/folder/other-document'],
            result_paths(response.json())
        )

    def test_keyword_index_str_query_and(self):
        query = {
            'test_list_field.query': ['Keyword1', 'Keyword2'],
            'test_list_field.operator': 'and',
        }
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/folder/doc'],
            result_paths(response.json())
        )

    def test_keyword_index_int_query(self):
        self.doc.test_list_field = [42, 23]
        self.doc.reindexObject()
        transaction.commit()

        query = {'test_list_field:int': 42}
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/folder/doc'],
            result_paths(response.json())
        )

    # BooleanIndex

    def test_boolean_index_query(self):
        query = {'test_bool_field': True, 'portal_type': 'DXTestDocument'}
        response = self.api_session.get('/folder/search', params=query)
        self.assertEqual(
            [u'/plone/folder/doc'],
            result_paths(response.json())
        )

        query = {'test_bool_field': False, 'portal_type': 'DXTestDocument'}
        response = self.api_session.get('/folder/search', params=query)
        self.assertEqual(
            [u'/plone/folder/other-document'],
            result_paths(response.json())
        )

    # FieldIndex

    def test_field_index_int_query(self):
        query = {'test_int_field:int': 42}
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/folder/doc'],
            result_paths(response.json())
        )

    def test_field_index_int_range_query(self):
        query = {
            'test_int_field.query:int': [41, 43],
            'test_int_field.range': 'min:max',
        }
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/folder/doc'],
            result_paths(response.json())
        )

    # ExtendedPathIndex

    def test_extended_path_index_query(self):
        query = {'path': '/'.join(self.folder.getPhysicalPath())}

        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/folder',
             u'/plone/folder/doc',
             u'/plone/folder/other-document'],
            result_paths(response.json())
        )

    def test_extended_path_index_depth_limiting(self):
        lvl1 = createContentInContainer(self.portal, u'Folder', id=u'lvl1')
        lvl2 = createContentInContainer(lvl1, u'Folder', id=u'lvl2')
        createContentInContainer(lvl2, u'Folder', id=u'lvl3')
        transaction.commit()

        path = '/plone/lvl1'

        # Depth 0 - only object identified by path
        query = {'path.query': path, 'path.depth': 0}
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/lvl1'],
            result_paths(response.json()))

        # Depth 1 - immediate children
        query = {'path.query': path, 'path.depth': 1}
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/lvl1/lvl2'],
            result_paths(response.json()))

        # No depth - object itself and all children
        query = {'path': path}
        response = self.api_session.get('/search', params=query)

        self.assertSetEqual(
            {u'/plone/lvl1', u'/plone/lvl1/lvl2', u'/plone/lvl1/lvl2/lvl3'},
            set(result_paths(response.json())))

    # DateIndex

    def test_date_index_query(self):
        query = {'created': date(1950, 1, 1).isoformat()}
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/folder/doc'],
            result_paths(response.json())
        )

    def test_date_index_ranged_query(self):
        query = {
            'created.query': [date(1949, 1, 1).isoformat(),
                              date(1951, 1, 1).isoformat()],
            'created.range': 'min:max',
        }
        response = self.api_session.get('/search', params=query)

        self.assertEqual(
            [u'/plone/folder/doc'],
            result_paths(response.json())
        )

    # DateRangeIndex

    def test_date_range_index_query(self):
        query = {'effectiveRange': date(1997, 1, 1).isoformat()}
        response = self.api_session.get('/folder/search', params=query)

        self.assertEqual(
            [u'/plone/folder',
             u'/plone/folder/doc'],
            result_paths(response.json())
        )

    # DateRecurringIndex

    def test_date_recurring_index_query(self):
        from datetime import datetime
        createContentInContainer(
            self.folder, u'Event', id=u'event',
            title=u'Event',
            start=datetime(2013, 1, 1, 0, 0),
            end=datetime(2013, 1, 1, 23, 59),
            whole_day=True,
            recurrence='FREQ=DAILY;COUNT=10;INTERVAL=2',
            timezone='UTC',
        )
        import transaction
        transaction.commit()

        # First occurrence
        query = {'start': date(2013, 1, 1).isoformat()}
        response = self.api_session.get('/folder/search', params=query)

        self.assertEqual(
            [u'/plone/folder/event'],
            result_paths(response.json())
        )

        # No event that day
        query = {'start': date(2013, 1, 2).isoformat()}
        response = self.api_session.get('/folder/search', params=query)

        self.assertEqual(
            [],
            result_paths(response.json())
        )

        # Second occurrence
        query = {'start': date(2013, 1, 3).isoformat()}
        response = self.api_session.get('/folder/search', params=query)

        self.assertEqual(
            [u'/plone/folder/event'],
            result_paths(response.json())
        )

        # Ranged query
        query = {
            'start.query': [date(2013, 1, 1).isoformat(),
                            date(2013, 1, 5).isoformat()],
            'start.range': 'min:max',
        }
        response = self.api_session.get('/folder/search', params=query)

        self.assertEqual(
            [u'/plone/folder/event'],
            result_paths(response.json())
        )

    # UUIDIndex

    def test_uuid_index_query(self):
        IMutableUUID(self.doc).set('7777a074cb4240d08c9a129e3a837777')
        self.doc.reindexObject()
        transaction.commit()

        query = {'UID': '7777a074cb4240d08c9a129e3a837777'}
        response = self.api_session.get('/search', params=query)
        self.assertEqual(
            [u'/plone/folder/doc'],
            result_paths(response.json())
        )
