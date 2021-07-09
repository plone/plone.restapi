from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.restapi.batching import DEFAULT_BATCH_SIZE
from plone.restapi.batching import HypermediaBatch
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.testing import RelativeSession
from plone.restapi.tests.helpers import result_paths
from urllib.parse import parse_qsl
from urllib.parse import urlparse

import transaction
import unittest


class TestBatchingDXBase(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def _create_doc(self, container, number):
        createContentInContainer(
            container,
            "DXTestDocument",
            id="doc-%s" % str(number + 1),
            title="Document %s" % str(number + 1),
        )


class TestBatchingSearch(TestBatchingDXBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()

        folder = createContentInContainer(self.portal, "Folder", id="folder")

        for i in range(5):
            self._create_doc(folder, i)
        transaction.commit()

    def test_contains_canonical_url(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/folder/@search?b_start=2&b_size=2")

        # Response should contain canonical URL without batching params
        self.assertEqual(response.json()["@id"], self.portal_url + "/folder/@search")

    def test_canonical_url_preserves_multiple_metadata_fields(self):
        qs = "b_start=2&b_size=2&metadata_fields=one&metadata_fields=two"
        response = self.api_session.get("/folder/@search?%s" % qs)

        # Response should contain canonical URL without batching params.
        # Argument lists like metadata_fields (same query string parameter
        # repeated multiple times) should be preserved.

        original_qs = parse_qsl(qs)
        canonicalized_qs = parse_qsl(urlparse(response.json()["@id"]).query)

        self.assertEqual(
            set(original_qs) - {("b_size", "2"), ("b_start", "2")},
            set(canonicalized_qs),
        )

    def test_contains_batching_links(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/folder/@search?b_start=2&b_size=2")

        # Batch info in response should contain appropriate batching links
        batch_info = response.json()["batching"]

        self.assertDictEqual(
            {
                "@id": self.portal_url + "/folder/@search?b_start=2&b_size=2",
                "first": self.portal_url + "/folder/@search?b_start=0&b_size=2",
                "next": self.portal_url + "/folder/@search?b_start=4&b_size=2",
                "prev": self.portal_url + "/folder/@search?b_start=0&b_size=2",
                "last": self.portal_url + "/folder/@search?b_start=4&b_size=2",
            },
            batch_info,
        )

    def test_contains_correct_batch_of_items(self):
        # Fetch the second page of the batch
        response = self.api_session.get(
            "/folder/@search?sort_on=path&b_start=2&b_size=2"
        )

        # Response should contain second batch of items
        self.assertEqual(
            ["/plone/folder/doc-2", "/plone/folder/doc-3"],
            result_paths(response.json()),
        )

    def test_total_item_count_is_correct(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/folder/@search?b_start=2&b_size=2")

        # Total count of items should be in items_total
        self.assertEqual(6, response.json()["items_total"])


class TestBatchingCollections(TestBatchingDXBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()

        folder = createContentInContainer(self.portal, "Folder", id="folder")

        for i in range(5):
            self._create_doc(folder, i)

        collection = createContentInContainer(
            self.portal, "Collection", id="collection"
        )
        collection.query = [
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.path",
                "v": "/plone/folder/",
            }
        ]
        transaction.commit()

    def test_contains_canonical_url(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/collection?b_start=2&b_size=2")

        # Response should contain canonical URL without batching params
        self.assertEqual(response.json()["@id"], self.portal_url + "/collection")

    def test_contains_batching_links(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/collection?b_start=2&b_size=2")

        # Batch info in response should contain appropriate batching links
        batch_info = response.json()["batching"]

        self.assertDictEqual(
            {
                "@id": self.portal_url + "/collection?b_start=2&b_size=2",
                "first": self.portal_url + "/collection?b_start=0&b_size=2",
                "next": self.portal_url + "/collection?b_start=4&b_size=2",
                "prev": self.portal_url + "/collection?b_start=0&b_size=2",
                "last": self.portal_url + "/collection?b_start=4&b_size=2",
            },
            batch_info,
        )

    def test_contains_correct_batch_of_items(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/collection?b_start=2&b_size=2")

        # Response should contain second batch of items
        _result_paths = result_paths(response.json())
        self.assertEqual(2, len(_result_paths))
        self.assertTrue(
            all(path.startswith("/plone/folder/doc-") for path in _result_paths)
        )

    def test_total_item_count_is_correct(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/collection?b_start=2&b_size=2")

        # Total count of items should be in items_total
        self.assertEqual(6, response.json()["items_total"])

    def test_batching_links_omitted_if_resulset_fits_in_single_batch(self):
        response = self.api_session.get("/collection?b_size=100")
        self.assertNotIn("batching", list(response.json()))


class TestBatchingDXFolders(TestBatchingDXBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()

        folder = createContentInContainer(self.portal, "Folder", id="folder")

        for i in range(5):
            self._create_doc(folder, i)
        transaction.commit()

    def test_contains_canonical_url(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/folder?b_start=2&b_size=2")

        # Response should contain canonical URL without batching params
        self.assertEqual(response.json()["@id"], self.portal_url + "/folder")

    def test_contains_batching_links(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/folder?b_start=2&b_size=2")

        # Batch info in response should contain appropriate batching links
        batch_info = response.json()["batching"]

        self.assertDictEqual(
            {
                "@id": self.portal_url + "/folder?b_start=2&b_size=2",
                "first": self.portal_url + "/folder?b_start=0&b_size=2",
                "next": self.portal_url + "/folder?b_start=4&b_size=2",
                "prev": self.portal_url + "/folder?b_start=0&b_size=2",
                "last": self.portal_url + "/folder?b_start=4&b_size=2",
            },
            batch_info,
        )

    def test_contains_correct_batch_of_items(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/folder?b_start=2&b_size=2")

        # Response should contain second batch of items
        _result_paths = result_paths(response.json())
        self.assertEqual(2, len(_result_paths))
        self.assertTrue(
            all(path.startswith("/plone/folder/doc-") for path in _result_paths)
        )

    def test_total_item_count_is_correct(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/folder?b_start=2&b_size=2")

        # Total count of items should be in items_total
        self.assertEqual(5, response.json()["items_total"])

    def test_batching_links_omitted_if_resulset_fits_in_single_batch(self):
        response = self.api_session.get("/folder?b_size=100")
        self.assertNotIn("batching", list(response.json()))

    def test_contains_batching_links_using_fullobjects(self):
        # Fetch the second page of the batch using fullobjects
        response = self.api_session.get("/folder?b_start=2&b_size=2&fullobjects")

        # Batch info in response should contain appropriate batching links
        batch_info = response.json()["batching"]

        self.assertDictEqual(
            {
                "@id": self.portal_url + "/folder?b_start=2&b_size=2&fullobjects",
                "first": self.portal_url + "/folder?b_start=0&b_size=2&fullobjects=",
                "next": self.portal_url + "/folder?b_start=4&b_size=2&fullobjects=",
                "prev": self.portal_url + "/folder?b_start=0&b_size=2&fullobjects=",
                "last": self.portal_url + "/folder?b_start=4&b_size=2&fullobjects=",
            },
            batch_info,
        )


class TestBatchingSiteRoot(TestBatchingDXBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()

        for i in range(5):
            self._create_doc(self.portal, i)
        transaction.commit()

    def test_contains_canonical_url(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/?b_start=2&b_size=2")

        # Response should contain canonical URL without batching params
        self.assertEqual(response.json()["@id"], self.portal_url + "/")

    def test_contains_batching_links(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/?b_start=2&b_size=2")

        # Batch info in response should contain appropriate batching links
        batch_info = response.json()["batching"]

        self.assertDictEqual(
            {
                "@id": self.portal_url + "/?b_start=2&b_size=2",
                "first": self.portal_url + "/?b_start=0&b_size=2",
                "next": self.portal_url + "/?b_start=4&b_size=2",
                "prev": self.portal_url + "/?b_start=0&b_size=2",
                "last": self.portal_url + "/?b_start=4&b_size=2",
            },
            batch_info,
        )

    def test_contains_correct_batch_of_items(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/?b_start=2&b_size=2")

        # Response should contain second batch of items
        _result_paths = result_paths(response.json())
        self.assertEqual(2, len(_result_paths))
        self.assertTrue(all(path.startswith("/plone/doc-") for path in _result_paths))

    def test_total_item_count_is_correct(self):
        # Fetch the second page of the batch
        response = self.api_session.get("/?b_start=2&b_size=2")

        # Total count of items should be in items_total
        self.assertEqual(5, response.json()["items_total"])

    def test_batching_links_omitted_if_resulset_fits_in_single_batch(self):
        response = self.api_session.get("/folder?b_size=100")
        self.assertNotIn("batching", list(response.json()))


class TestHypermediaBatch(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.portal.REQUEST

    def test_items_total(self):
        items = list(range(1, 26))
        self.request.form["b_size"] = 10
        batch = HypermediaBatch(self.request, items)
        # items_total should be total number of items in the sequence
        self.assertEqual(25, batch.items_total)

    def test_default_batch_size(self):
        items = list(range(1, 27))
        batch = HypermediaBatch(self.request, items)
        self.assertEqual(DEFAULT_BATCH_SIZE, len(list(batch)))

    def test_custom_batch_size(self):
        items = list(range(1, 26))
        self.request.form["b_size"] = 5
        batch = HypermediaBatch(self.request, items)
        # Batch size should be customizable via request
        self.assertEqual(5, len(list(batch)))

    def test_default_batch_start(self):
        items = list(range(1, 26))
        self.request.form["b_size"] = 10
        batch = HypermediaBatch(self.request, items)
        # Batch should start on first item by default
        self.assertEqual(list(range(1, 11)), list(batch))

    def test_custom_batch_start(self):
        items = list(range(1, 26))
        self.request.form["b_size"] = 10
        self.request.form["b_start"] = 5
        batch = HypermediaBatch(self.request, items)
        # Batch start should be customizable via request
        self.assertEqual(list(range(6, 16)), list(batch))

    def test_custom_start_and_size_can_be_combined(self):
        items = list(range(1, 26))
        self.request.form["b_size"] = 5
        self.request.form["b_start"] = 5
        batch = HypermediaBatch(self.request, items)
        # Should be able to combine custom batch start and size
        self.assertListEqual(list(range(6, 11)), list(batch))

    def test_canonical_url(self):
        items = list(range(1, 26))
        self.request.form["b_size"] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertEqual("http://nohost", batch.canonical_url)

    def test_canonical_url_preserves_query_string_params(self):
        items = list(range(1, 26))

        self.request.form["b_size"] = 10
        self.request["QUERY_STRING"] = "one=1&two=2"
        batch = HypermediaBatch(self.request, items)

        parsed_url = urlparse(batch.canonical_url)
        qs_params = dict(parse_qsl(parsed_url.query))

        self.assertEqual({"one": "1", "two": "2"}, qs_params)
        self.assertEqual("nohost", parsed_url.netloc)
        self.assertEqual("", parsed_url.path)

    def test_canonical_url_preserves_list_like_query_string_params(self):
        items = list(range(1, 26))

        self.request.form["b_size"] = 10
        self.request["QUERY_STRING"] = "foolist=1&foolist=2"
        batch = HypermediaBatch(self.request, items)

        # Argument lists (same query string parameter repeated multiple
        # times) should be preserved.

        self.assertEqual(
            {("foolist", "1"), ("foolist", "2")},
            set(parse_qsl(urlparse(batch.canonical_url).query)),
        )

    def test_canonical_url_strips_batching_params(self):
        items = list(range(1, 26))

        self.request.form["b_size"] = 10
        self.request["QUERY_STRING"] = "one=1&b_size=10&b_start=20&two=2"
        batch = HypermediaBatch(self.request, items)

        parsed_url = urlparse(batch.canonical_url)
        qs_params = dict(parse_qsl(parsed_url.query))

        self.assertEqual({"one": "1", "two": "2"}, qs_params)
        self.assertEqual("nohost", parsed_url.netloc)
        self.assertEqual("", parsed_url.path)

    def test_canonical_url_strips_sorting_params(self):
        items = list(range(1, 26))

        self.request["QUERY_STRING"] = "one=1&sort_on=path&two=2"
        batch = HypermediaBatch(self.request, items)

        parsed_url = urlparse(batch.canonical_url)
        qs_params = dict(parse_qsl(parsed_url.query))

        self.assertEqual({"one": "1", "two": "2"}, qs_params)
        self.assertEqual("nohost", parsed_url.netloc)
        self.assertEqual("", parsed_url.path)

    def test_current_batch_url(self):
        items = list(range(1, 26))

        self.request.form["b_size"] = 10
        self.request["ACTUAL_URL"] = "http://nohost"
        self.request["QUERY_STRING"] = "b_size=10&b_start=20"
        batch = HypermediaBatch(self.request, items)
        self.assertEqual("http://nohost?b_size=10&b_start=20", batch.current_batch_url)

    def test_batching_links_omitted_if_resultset_fits_in_single_batch(self):
        items = list(range(1, 5))

        self.request.form["b_size"] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertEqual(None, batch.links)

    def test_first_link_contained(self):
        items = list(range(1, 26))

        self.request.form["b_size"] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertDictContainsSubset({"first": "http://nohost?b_start=0"}, batch.links)

    def test_first_link_preserves_list_like_querystring_params(self):
        items = list(range(1, 26))

        self.request.form["b_size"] = 10
        self.request["QUERY_STRING"] = "foolist=1&foolist=2"
        batch = HypermediaBatch(self.request, items)

        # Argument lists (same query string parameter repeated multiple
        # times) should be preserved.

        batch_params = {("b_start", "0"), ("b_size", "10")}
        self.assertEqual(
            {("foolist", "1"), ("foolist", "2")},
            set(parse_qsl(urlparse(batch.links["first"]).query)) - batch_params,
        )

    def test_last_link_contained(self):
        items = list(range(1, 26))

        self.request.form["b_size"] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertDictContainsSubset({"last": "http://nohost?b_start=20"}, batch.links)

    def test_next_link_contained_if_necessary(self):
        items = list(range(1, 26))

        self.request.form["b_size"] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertDictContainsSubset({"next": "http://nohost?b_start=10"}, batch.links)

    def test_next_link_omitted_on_last_page(self):
        items = list(range(1, 26))

        # Start on last page
        self.request.form["b_size"] = 10
        self.request.form["b_start"] = 20
        batch = HypermediaBatch(self.request, items)
        self.assertSetEqual({"@id", "first", "prev", "last"}, set(batch.links))

    def test_prev_link_contained_if_necessary(self):
        items = list(range(1, 26))

        # Start on third page
        self.request.form["b_size"] = 10
        self.request.form["b_start"] = 20
        batch = HypermediaBatch(self.request, items)
        self.assertDictContainsSubset({"prev": "http://nohost?b_start=10"}, batch.links)

    def test_prev_link_omitted_on_first_page(self):
        items = list(range(1, 26))

        self.request.form["b_size"] = 10
        batch = HypermediaBatch(self.request, items)
        self.assertSetEqual({"@id", "first", "next", "last"}, set(batch.links))

    def test_no_gaps_or_duplicates_between_pages(self):
        items = list(range(1, 26))
        items_from_all_batches = []

        size = 10
        self.request.form["b_size"] = size

        for pagenumber in range(3):
            self.request.form["b_start"] = pagenumber * size
            batch = HypermediaBatch(self.request, items)
            items_from_all_batches.extend(list(batch))

        self.assertEqual(items, items_from_all_batches)

    def test_batch_start_never_drops_below_zero(self):
        items = list(range(1, 26))

        # Start in the middle of what would otherwise be the first batch
        self.request.form["b_size"] = 10
        self.request.form["b_start"] = 5
        batch = HypermediaBatch(self.request, items)
        self.assertEqual("http://nohost?b_start=0", batch.links["prev"])
