# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.batching import DEFAULT_BATCH_SIZE
from plone.restapi.batching import HypermediaBatch
from plone.restapi.testing import PLONE_RESTAPI_AT_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.testing import RelativeSession
from plone.restapi.tests.helpers import result_paths
from urlparse import parse_qsl
from urlparse import urlparse

import transaction
import unittest


class TestBatchingDXBase(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def _create_doc(self, container, number):
        createContentInContainer(
            container, u'DXTestDocument',
            id='doc-%s' % str(number + 1),
            title=u'Document %s' % str(number + 1),
            created=DateTime(1975, 1, 1, 0, 0),
            effective=DateTime(2015, 1, 1, 0, 0),
            expires=DateTime(2020, 1, 1, 0, 0),
        )


class TestBatchingSearch(TestBatchingDXBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestBatchingSearch, self).setUp()

        folder = createContentInContainer(
            self.portal, u'Folder',
            id=u'folder')

        for i in range(5):
            self._create_doc(folder, i)
        transaction.commit()

    def test_contains_canonical_url(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder/@search?b_start=2&b_size=2')

        # Response should contain canonical URL without batching params
        self.assertEqual(
            response.json()['@id'],
            self.portal_url + '/folder/@search')

    def test_contains_batching_links(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder/@search?b_start=2&b_size=2')

        # Batch info in response should contain appropriate batching links
        batch_info = response.json()['batching']

        self.assertDictEqual(
            {u'@id': self.portal_url + '/folder/@search?b_start=2&b_size=2',
             u'first': self.portal_url + '/folder/@search?b_size=2&b_start=0',
             u'next': self.portal_url + '/folder/@search?b_size=2&b_start=4',
             u'prev': self.portal_url + '/folder/@search?b_size=2&b_start=0',
             u'last': self.portal_url + '/folder/@search?b_size=2&b_start=4',
             },
            batch_info)

    def test_contains_correct_batch_of_items(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder/@search?b_start=2&b_size=2')

        # Response should contain second batch of items
        self.assertEquals([
            u'/plone/folder/doc-2',
            u'/plone/folder/doc-3'],
            result_paths(response.json()))

    def test_total_item_count_is_correct(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder/@search?b_start=2&b_size=2')

        # Total count of items should be in items_total
        self.assertEqual(6, response.json()['items_total'])


class TestBatchingCollections(TestBatchingDXBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestBatchingCollections, self).setUp()

        folder = createContentInContainer(
            self.portal, u'Folder',
            id=u'folder')

        for i in range(5):
            self._create_doc(folder, i)

        collection = createContentInContainer(
            self.portal, u'Collection',
            id='collection')
        collection.query = [
            {"i": "path",
             "o": "plone.app.querystring.operation.string.path",
             "v": "/plone/folder/"},
        ]
        transaction.commit()

    def test_contains_canonical_url(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/collection?b_start=2&b_size=2')

        # Response should contain canonical URL without batching params
        self.assertEqual(
            response.json()['@id'],
            self.portal_url + '/collection')

    def test_contains_batching_links(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/collection?b_start=2&b_size=2')

        # Batch info in response should contain appropriate batching links
        batch_info = response.json()['batching']

        self.assertDictEqual(
            {u'@id': self.portal_url + '/collection?b_start=2&b_size=2',
             u'first': self.portal_url + '/collection?b_size=2&b_start=0',
             u'next': self.portal_url + '/collection?b_size=2&b_start=4',
             u'prev': self.portal_url + '/collection?b_size=2&b_start=0',
             u'last': self.portal_url + '/collection?b_size=2&b_start=4',
             },
            batch_info)

    def test_contains_correct_batch_of_items(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/collection?b_start=2&b_size=2')

        # Response should contain second batch of items
        self.assertEquals([
            u'/plone/folder/doc-2',
            u'/plone/folder/doc-3'],
            result_paths(response.json()))

    def test_total_item_count_is_correct(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/collection?b_start=2&b_size=2')

        # Total count of items should be in items_total
        self.assertEqual(6, response.json()['items_total'])

    def test_batching_links_omitted_if_resulset_fits_in_single_batch(self):
        response = self.api_session.get('/collection?b_size=100')
        self.assertNotIn('batching', response.json().keys())


class TestBatchingDXFolders(TestBatchingDXBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestBatchingDXFolders, self).setUp()

        folder = createContentInContainer(
            self.portal, u'Folder',
            id=u'folder')

        for i in range(5):
            self._create_doc(folder, i)
        transaction.commit()

    def test_contains_canonical_url(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder?b_start=2&b_size=2')

        # Response should contain canonical URL without batching params
        self.assertEqual(
            response.json()['@id'],
            self.portal_url + '/folder')

    def test_contains_batching_links(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder?b_start=2&b_size=2')

        # Batch info in response should contain appropriate batching links
        batch_info = response.json()['batching']

        self.assertDictEqual(
            {u'@id': self.portal_url + '/folder?b_start=2&b_size=2',
             u'first': self.portal_url + '/folder?b_size=2&b_start=0',
             u'next': self.portal_url + '/folder?b_size=2&b_start=4',
             u'prev': self.portal_url + '/folder?b_size=2&b_start=0',
             u'last': self.portal_url + '/folder?b_size=2&b_start=4',
             },
            batch_info)

    def test_contains_correct_batch_of_items(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder?b_start=2&b_size=2')

        # Response should contain second batch of items
        self.assertEquals([
            u'/plone/folder/doc-3',
            u'/plone/folder/doc-4'],
            result_paths(response.json()))

    def test_total_item_count_is_correct(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder?b_start=2&b_size=2')

        # Total count of items should be in items_total
        self.assertEqual(5, response.json()['items_total'])

    def test_batching_links_omitted_if_resulset_fits_in_single_batch(self):
        response = self.api_session.get('/folder?b_size=100')
        self.assertNotIn('batching', response.json().keys())


class TestBatchingSiteRoot(TestBatchingDXBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestBatchingSiteRoot, self).setUp()

        for i in range(5):
            self._create_doc(self.portal, i)
        transaction.commit()

    def test_contains_canonical_url(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/?b_start=2&b_size=2')

        # Response should contain canonical URL without batching params
        self.assertEqual(
            response.json()['@id'],
            u'http://localhost:55001/plone/')

    def test_contains_batching_links(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/?b_start=2&b_size=2')

        # Batch info in response should contain appropriate batching links
        batch_info = response.json()['batching']

        self.assertDictEqual(
            {u'@id': self.portal_url + '/?b_start=2&b_size=2',
             u'first': self.portal_url + '/?b_size=2&b_start=0',
             u'next': self.portal_url + '/?b_size=2&b_start=4',
             u'prev': self.portal_url + '/?b_size=2&b_start=0',
             u'last': self.portal_url + '/?b_size=2&b_start=4',
             },
            batch_info)

    def test_contains_correct_batch_of_items(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/?b_start=2&b_size=2')

        # Response should contain second batch of items
        self.assertEquals([
            u'/plone/doc-3',
            u'/plone/doc-4'],
            result_paths(response.json()))

    def test_total_item_count_is_correct(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/?b_start=2&b_size=2')

        # Total count of items should be in items_total
        self.assertEqual(5, response.json()['items_total'])

    def test_batching_links_omitted_if_resulset_fits_in_single_batch(self):
        response = self.api_session.get('/folder?b_size=100')
        self.assertNotIn('batching', response.json().keys())


class TestBatchingArchetypes(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST

        setRoles(self.portal, TEST_USER_ID, ['Member', 'Contributor'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        folder = self.portal[self.portal.invokeFactory(
            'Folder',
            id='folder',
            title='Some Folder',
        )]

        for i in range(5):
            self._create_doc(folder, i)
        transaction.commit()

    def _create_doc(self, container, number):
        container.invokeFactory(
            'Document',
            id='doc-%s' % str(number + 1),
            title='Document %s' % str(number + 1),
        )

    def test_contains_canonical_url(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder?b_start=2&b_size=2')

        # Response should contain canonical URL without batching params
        self.assertEqual(
            response.json()['@id'],
            self.portal_url + '/folder')

    def test_contains_batching_links(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder?b_start=2&b_size=2')

        # Batch info in response should contain appropriate batching links
        batch_info = response.json()['batching']

        self.assertDictEqual(
            {u'@id': self.portal_url + '/folder?b_start=2&b_size=2',
             u'first': self.portal_url + '/folder?b_size=2&b_start=0',
             u'next': self.portal_url + '/folder?b_size=2&b_start=4',
             u'prev': self.portal_url + '/folder?b_size=2&b_start=0',
             u'last': self.portal_url + '/folder?b_size=2&b_start=4',
             },
            batch_info)

    def test_contains_correct_batch_of_items(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder?b_start=2&b_size=2')

        # Response should contain second batch of items
        self.assertEquals([
            u'/plone/folder/doc-3',
            u'/plone/folder/doc-4'],
            result_paths(response.json()))

    def test_total_item_count_is_correct(self):
        # Fetch the second page of the batch
        response = self.api_session.get('/folder?b_start=2&b_size=2')

        # Total count of items should be in items_total
        self.assertEqual(5, response.json()['items_total'])

    def test_batching_links_omitted_if_resulset_fits_in_single_batch(self):
        response = self.api_session.get('/folder?b_size=100')
        self.assertNotIn('batching', response.json().keys())


class TestHypermediaBatch(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST

    def test_items_total(self):
        items = range(1, 26)
        self.request.form['b_size'] = 10
        batch = HypermediaBatch(self.request, items)
        # items_total should be total number of items in the sequence
        self.assertEqual(
            25, batch.items_total)

    def test_default_batch_size(self):
        items = range(1, 27)
        batch = HypermediaBatch(self.request, items)
        self.assertEqual(DEFAULT_BATCH_SIZE, len(list(batch)))

    def test_custom_batch_size(self):
        items = range(1, 26)
        self.request.form['b_size'] = 5
        batch = HypermediaBatch(self.request, items)
        # Batch size should be customizable via request
        self.assertEqual(
            5, len(list(batch)))

    def test_default_batch_start(self):
        items = range(1, 26)
        self.request.form['b_size'] = 10
        batch = HypermediaBatch(self.request, items)
        # Batch should start on first item by default
        self.assertEqual(
            range(1, 11), list(batch))

    def test_custom_batch_start(self):
        items = range(1, 26)
        self.request.form['b_size'] = 10
        self.request.form['b_start'] = 5
        batch = HypermediaBatch(self.request, items)
        # Batch start should be customizable via request
        self.assertEqual(
            range(6, 16), list(batch))

    def test_custom_start_and_size_can_be_combined(self):
        items = range(1, 26)
        self.request.form['b_size'] = 5
        self.request.form['b_start'] = 5
        batch = HypermediaBatch(self.request, items)
        # Should be able to combine custom batch start and size
        self.assertListEqual(
            range(6, 11), list(batch))

    def test_canonical_url(self):
        items = range(1, 26)
        self.request.form['b_size'] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertEqual('http://nohost', batch.canonical_url)

    def test_canonical_url_preserves_query_string_params(self):
        items = range(1, 26)

        self.request.form['b_size'] = 10
        self.request['QUERY_STRING'] = 'one=1&two=2'
        batch = HypermediaBatch(self.request, items)

        parsed_url = urlparse(batch.canonical_url)
        qs_params = dict(parse_qsl(parsed_url.query))

        self.assertEquals({'one': '1', 'two': '2'}, qs_params)
        self.assertEquals('nohost', parsed_url.netloc)
        self.assertEquals('', parsed_url.path)

    def test_canonical_url_strips_batching_params(self):
        items = range(1, 26)

        self.request.form['b_size'] = 10
        self.request['QUERY_STRING'] = 'one=1&b_size=10&b_start=20&two=2'
        batch = HypermediaBatch(self.request, items)

        parsed_url = urlparse(batch.canonical_url)
        qs_params = dict(parse_qsl(parsed_url.query))

        self.assertEquals({'one': '1', 'two': '2'}, qs_params)
        self.assertEquals('nohost', parsed_url.netloc)
        self.assertEquals('', parsed_url.path)

    def test_canonical_url_strips_sorting_params(self):
        items = range(1, 26)

        self.request['QUERY_STRING'] = 'one=1&sort_on=path&two=2'
        batch = HypermediaBatch(self.request, items)

        parsed_url = urlparse(batch.canonical_url)
        qs_params = dict(parse_qsl(parsed_url.query))

        self.assertEquals({'one': '1', 'two': '2'}, qs_params)
        self.assertEquals('nohost', parsed_url.netloc)
        self.assertEquals('', parsed_url.path)

    def test_current_batch_url(self):
        items = range(1, 26)

        self.request.form['b_size'] = 10
        self.request['ACTUAL_URL'] = 'http://nohost'
        self.request['QUERY_STRING'] = 'b_size=10&b_start=20'
        batch = HypermediaBatch(self.request, items)
        self.assertEqual(
            'http://nohost?b_size=10&b_start=20', batch.current_batch_url)

    def test_batching_links_omitted_if_resultset_fits_in_single_batch(self):
        items = range(1, 5)

        self.request.form['b_size'] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertEqual(None, batch.links)

    def test_first_link_contained(self):
        items = range(1, 26)

        self.request.form['b_size'] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertDictContainsSubset(
            {'first': 'http://nohost?b_start=0'}, batch.links)

    def test_last_link_contained(self):
        items = range(1, 26)

        self.request.form['b_size'] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertDictContainsSubset(
            {'last': 'http://nohost?b_start=20'}, batch.links)

    def test_next_link_contained_if_necessary(self):
        items = range(1, 26)

        self.request.form['b_size'] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertDictContainsSubset(
            {'next': 'http://nohost?b_start=10'}, batch.links)

    def test_next_link_omitted_on_last_page(self):
        items = range(1, 26)

        # Start on last page
        self.request.form['b_size'] = 10
        self.request.form['b_start'] = 20
        batch = HypermediaBatch(self.request, items)
        self.assertSetEqual(
            set(['@id', 'first', 'prev', 'last']),
            set(batch.links.keys()))

    def test_prev_link_contained_if_necessary(self):
        items = range(1, 26)

        # Start on third page
        self.request.form['b_size'] = 10
        self.request.form['b_start'] = 20
        batch = HypermediaBatch(self.request, items)
        self.assertDictContainsSubset(
            {'prev': 'http://nohost?b_start=10'}, batch.links)

    def test_prev_link_omitted_on_first_page(self):
        items = range(1, 26)

        self.request.form['b_size'] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertSetEqual(
            set(['@id', 'first', 'next', 'last']),
            set(batch.links.keys()))

    def test_no_gaps_or_duplicates_between_pages(self):
        items = range(1, 26)
        items_from_all_batches = []

        size = 10
        self.request.form['b_size'] = size

        for pagenumber in range(3):
            self.request.form['b_start'] = pagenumber * size
            batch = HypermediaBatch(self.request, items)
            items_from_all_batches.extend(list(batch))

        self.assertEqual(items, items_from_all_batches)

    def test_batch_start_never_drops_below_zero(self):
        items = range(1, 26)

        # Start in the middle of what would otherwise be the first batch
        self.request.form['b_size'] = 10
        self.request.form['b_start'] = 5
        batch = HypermediaBatch(self.request, items)
        self.assertEquals(
            'http://nohost?b_start=0', batch.links['prev'])
