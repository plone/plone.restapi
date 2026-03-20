from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_PASSWORD
from plone.base.interfaces.recyclebin import IRecycleBin
from plone.base.interfaces.recyclebin import IRecycleBinControlPanelSettings
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getUtility

import plone.api as api
import transaction
import unittest


class RecycleBinTestBase(unittest.TestCase):
    """Base class for recyclebin service tests that handles common setup."""

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        # Enable recycle bin
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IRecycleBinControlPanelSettings, prefix="recyclebin-controlpanel"
        )
        settings.recycling_enabled = True
        settings.retention_period = 30
        settings.restore_to_initial_state = False

        # Clear the recycle bin before each test
        recyclebin = getUtility(IRecycleBin)
        recyclebin.clear()

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def _delete_to_recyclebin(self, obj):
        """Delete obj via manage_delObjects so the event handler populates the bin.
        Returns the recycle_id assigned by the event handler."""
        recyclebin = getUtility(IRecycleBin)
        items_before = {item["recycle_id"] for item in recyclebin.get_items()}
        obj.aq_parent.manage_delObjects([obj.getId()])
        transaction.commit()
        items_after = {item["recycle_id"] for item in recyclebin.get_items()}
        new_ids = items_after - items_before
        return new_ids.pop() if new_ids else None

    def _add_document_to_recyclebin(self, doc_id="test-doc", doc_title="Test Document"):
        """Helper: create a document, delete it so the event handler puts it in the
        recyclebin, and return (recycle_id, original_title)."""
        self.portal.invokeFactory("Document", doc_id, title=doc_title)
        doc = self.portal[doc_id]
        recycle_id = self._delete_to_recyclebin(doc)
        return recycle_id, doc_title

    def _add_folder_to_recyclebin(
        self, folder_id="test-folder", folder_title="Test Folder"
    ):
        """Helper: create a folder with a child document, delete it so the event
        handler puts it in the recyclebin, and return (recycle_id, original_title)."""
        self.portal.invokeFactory("Folder", folder_id, title=folder_title)
        folder = self.portal[folder_id]
        folder.invokeFactory("Document", "child-doc", title="Child Document")
        recycle_id = self._delete_to_recyclebin(folder)
        return recycle_id, folder_title

    def _disable_recyclebin(self):
        """Helper: disable the recycle bin and commit."""
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IRecycleBinControlPanelSettings, prefix="recyclebin-controlpanel"
        )
        settings.recycling_enabled = False
        transaction.commit()


class TestRecycleBinGET(RecycleBinTestBase):
    """Tests for GET /@recyclebin (list) and GET /@recyclebin/{item_id} (single item)."""

    # ------------------------------------------------------------------
    # Listing tests
    # ------------------------------------------------------------------

    def test_get_empty_recyclebin_returns_200(self):
        """GET /@recyclebin on empty bin returns 200 with empty items list."""
        response = self.api_session.get("/@recyclebin")
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertEqual(0, data["items_total"])
        self.assertEqual([], data["items"])

    def test_get_listing_returns_expected_keys(self):
        """GET /@recyclebin listing contains required top-level keys."""
        response = self.api_session.get("/@recyclebin")
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertIn("@id", data)
        self.assertIn("items_total", data)
        self.assertIn("items", data)

    def test_get_listing_with_items(self):
        """GET /@recyclebin lists deleted items."""
        self._add_document_to_recyclebin()
        response = self.api_session.get("/@recyclebin")
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertEqual(1, data["items_total"])
        self.assertEqual(1, len(data["items"]))

    def test_get_listing_item_structure(self):
        """Each item in GET /@recyclebin listing contains the expected keys."""
        self._add_document_to_recyclebin(doc_title="My Page")
        response = self.api_session.get("/@recyclebin")
        item = response.json()["items"][0]
        expected_keys = {
            "@id",
            "@type",
            "id",
            "title",
            "path",
            "parent_path",
            "deletion_date",
            "size",
            "recycle_id",
            "deleted_by",
            "language",
            "review_state",
            "has_children",
            "actions",
        }
        self.assertEqual(expected_keys, set(item.keys()))

    def test_get_listing_item_title_matches(self):
        """Item title in listing matches the original document title."""
        self._add_document_to_recyclebin(doc_title="My Special Page")
        response = self.api_session.get("/@recyclebin")
        item = response.json()["items"][0]
        self.assertEqual("My Special Page", item["title"])

    def test_get_listing_item_has_actions(self):
        """Items in listing expose restore and purge action URLs."""
        recycle_id, _title = self._add_document_to_recyclebin()
        response = self.api_session.get("/@recyclebin")
        item = response.json()["items"][0]
        self.assertIn("restore", item["actions"])
        self.assertIn("purge", item["actions"])
        self.assertIn(recycle_id, item["actions"]["restore"])
        self.assertIn(recycle_id, item["actions"]["purge"])

    def test_get_listing_folder_has_children_flag(self):
        """Folder with children has has_children=True in listing."""
        self._add_folder_to_recyclebin()
        response = self.api_session.get("/@recyclebin")
        item = response.json()["items"][0]
        self.assertTrue(item["has_children"])

    def test_get_listing_document_has_no_children(self):
        """Document entry has has_children=False in listing."""
        self._add_document_to_recyclebin()
        response = self.api_session.get("/@recyclebin")
        item = response.json()["items"][0]
        self.assertFalse(item["has_children"])

    # ------------------------------------------------------------------
    # Filtering tests
    # ------------------------------------------------------------------

    def test_filter_by_type(self):
        """portal_type parameter returns only items of matching portal_type."""
        self._add_document_to_recyclebin(doc_id="doc1", doc_title="Doc 1")
        self._add_folder_to_recyclebin(folder_id="folder1", folder_title="Folder 1")
        response = self.api_session.get("/@recyclebin?portal_type=Document")
        data = response.json()
        self.assertEqual(1, data["items_total"])
        self.assertEqual("Document", data["items"][0]["@type"])

    def test_filter_by_search_query_title(self):
        """title parameter filters by title."""
        self._add_document_to_recyclebin(doc_id="doc-alpha", doc_title="Alpha Document")
        self._add_document_to_recyclebin(doc_id="doc-beta", doc_title="Beta Document")
        response = self.api_session.get("/@recyclebin?title=alpha")
        data = response.json()
        self.assertEqual(1, data["items_total"])
        self.assertIn("Alpha", data["items"][0]["title"])

    def test_filter_by_has_subitems_with_subitems(self):
        """has_subitems=true returns only items with children."""
        self._add_document_to_recyclebin()
        self._add_folder_to_recyclebin()
        response = self.api_session.get("/@recyclebin?has_subitems=true")
        data = response.json()
        self.assertEqual(1, data["items_total"])
        self.assertTrue(data["items"][0]["has_children"])

    def test_filter_by_has_subitems_without_subitems(self):
        """has_subitems=false returns only items without children."""
        self._add_document_to_recyclebin()
        self._add_folder_to_recyclebin()
        response = self.api_session.get("/@recyclebin?has_subitems=false")
        data = response.json()
        self.assertEqual(1, data["items_total"])
        self.assertFalse(data["items"][0]["has_children"])

    def test_filter_no_match_returns_empty(self):
        """Filtering with a portal_type that doesn't exist returns empty items list."""
        self._add_document_to_recyclebin()
        response = self.api_session.get("/@recyclebin?portal_type=NonExistentType")
        data = response.json()
        self.assertEqual(0, data["items_total"])
        self.assertEqual([], data["items"])

    def test_filter_invalid_date_from_returns_bad_request(self):
        """A malformed date_from returns 400 BadRequest."""
        response = self.api_session.get("/@recyclebin?date_from=not-a-date")
        self.assertEqual(400, response.status_code)
        self.assertIn("date_from", response.json()["message"])

    def test_filter_invalid_date_to_returns_bad_request(self):
        """A malformed date_to returns 400 BadRequest."""
        response = self.api_session.get("/@recyclebin?date_to=31/12/2024")
        self.assertEqual(400, response.status_code)
        self.assertIn("date_to", response.json()["message"])

    # ------------------------------------------------------------------
    # Sorting tests
    # ------------------------------------------------------------------

    def test_sort_by_title_asc(self):
        """sort_on=title&sort_order=ascending returns items alphabetically ascending by title."""
        self._add_document_to_recyclebin(doc_id="doc-z", doc_title="Zebra")
        self._add_document_to_recyclebin(doc_id="doc-a", doc_title="Apple")
        response = self.api_session.get(
            "/@recyclebin?sort_on=title&sort_order=ascending"
        )
        titles = [item["title"] for item in response.json()["items"]]
        self.assertEqual(["Apple", "Zebra"], titles)

    def test_sort_by_title_desc(self):
        """sort_on=title&sort_order=descending returns items alphabetically descending by title."""
        self._add_document_to_recyclebin(doc_id="doc-z2", doc_title="Zebra")
        self._add_document_to_recyclebin(doc_id="doc-a2", doc_title="Apple")
        response = self.api_session.get(
            "/@recyclebin?sort_on=title&sort_order=descending"
        )
        titles = [item["title"] for item in response.json()["items"]]
        self.assertEqual(["Zebra", "Apple"], titles)

    # ------------------------------------------------------------------
    # Individual item tests
    # ------------------------------------------------------------------

    def test_get_individual_item_by_id(self):
        """GET /@recyclebin/{id} returns the specific deleted item."""
        recycle_id, _title = self._add_document_to_recyclebin(doc_title="Single Item")
        response = self.api_session.get(f"/@recyclebin/{recycle_id}")
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertEqual(recycle_id, data["recycle_id"])
        self.assertEqual("Single Item", data["title"])

    def test_get_individual_item_structure(self):
        """GET /@recyclebin/{id} contains the expected keys."""
        recycle_id, _title = self._add_document_to_recyclebin()
        response = self.api_session.get(f"/@recyclebin/{recycle_id}")
        data = response.json()
        expected_keys = {
            "@id",
            "id",
            "title",
            "@type",
            "path",
            "parent_path",
            "deletion_date",
            "size",
            "recycle_id",
            "deleted_by",
            "language",
            "review_state",
            "has_children",
            "children_count",
            "children",
            "actions",
        }
        self.assertEqual(expected_keys, set(data.keys()))

    def test_get_individual_item_not_found_returns_404(self):
        """GET /@recyclebin/{non-existent-id} returns 404."""
        response = self.api_session.get("/@recyclebin/this-id-does-not-exist")
        self.assertEqual(404, response.status_code)
        self.assertEqual("NotFound", response.json()["error"]["type"])

    def test_get_individual_item_folder_with_children(self):
        """GET /@recyclebin/{id} for a folder shows children details."""
        recycle_id, _title = self._add_folder_to_recyclebin()
        response = self.api_session.get(f"/@recyclebin/{recycle_id}")
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertTrue(data["has_children"])
        self.assertGreater(data["children_count"], 0)
        self.assertGreater(len(data["children"]), 0)

    def test_get_individual_item_children_structure(self):
        """Children entries in GET /@recyclebin/{id} have expected keys."""
        recycle_id, _title = self._add_folder_to_recyclebin()
        response = self.api_session.get(f"/@recyclebin/{recycle_id}")
        child = response.json()["children"][0]
        self.assertIn("id", child)
        self.assertIn("title", child)
        self.assertIn("@type", child)
        self.assertIn("path", child)
        self.assertIn("size", child)

    # ------------------------------------------------------------------
    # Disabled recycle bin
    # ------------------------------------------------------------------

    def test_get_listing_disabled_recyclebin_returns_404(self):
        """GET /@recyclebin returns 404 when recycle bin is disabled."""
        self._disable_recyclebin()
        response = self.api_session.get("/@recyclebin")
        self.assertEqual(404, response.status_code)
        self.assertEqual("NotFound", response.json()["error"]["type"])

    def test_get_item_disabled_recyclebin_returns_404(self):
        """GET /@recyclebin/{id} returns 404 when recycle bin is disabled."""
        self._disable_recyclebin()
        response = self.api_session.get("/@recyclebin/some-id")
        self.assertEqual(404, response.status_code)


class TestRecycleBinPurge(RecycleBinTestBase):
    """Tests for DELETE /@recyclebin/{item_id} and DELETE /@recyclebin."""

    def test_purge_single_item_returns_204(self):
        """DELETE /@recyclebin/{id} returns 204 No Content."""
        recycle_id, _title = self._add_document_to_recyclebin()
        response = self.api_session.delete(f"/@recyclebin/{recycle_id}")
        self.assertEqual(204, response.status_code)

    def test_purge_single_item_removes_item(self):
        """After DELETE /@recyclebin/{id} the item is no longer in the bin."""
        recycle_id, _title = self._add_document_to_recyclebin()
        self.api_session.delete(f"/@recyclebin/{recycle_id}")
        transaction.abort()  # sync with what the WSGI request committed
        recyclebin = getUtility(IRecycleBin)
        self.assertIsNone(recyclebin.get_item(recycle_id))

    def test_purge_nonexistent_item_returns_404(self):
        """DELETE /@recyclebin/{non-existent-id} returns 404."""
        response = self.api_session.delete("/@recyclebin/this-id-does-not-exist")
        self.assertEqual(404, response.status_code)
        self.assertEqual("NotFound", response.json()["error"]["type"])

    def test_purge_all_returns_204(self):
        """DELETE /@recyclebin (no item_id) empties the bin and returns 204."""
        self._add_document_to_recyclebin(doc_id="doc-purge-1", doc_title="D1")
        self._add_document_to_recyclebin(doc_id="doc-purge-2", doc_title="D2")
        response = self.api_session.delete("/@recyclebin")
        self.assertEqual(204, response.status_code)

    def test_purge_all_empties_bin(self):
        """After DELETE /@recyclebin the recycle bin is empty."""
        self._add_document_to_recyclebin(doc_id="doc-empty-1", doc_title="E1")
        self._add_document_to_recyclebin(doc_id="doc-empty-2", doc_title="E2")
        self.api_session.delete("/@recyclebin")
        transaction.abort()  # sync with what the WSGI request committed
        recyclebin = getUtility(IRecycleBin)
        self.assertEqual(0, len(recyclebin.get_items()))

    def test_purge_disabled_recyclebin_returns_404(self):
        """DELETE /@recyclebin returns 404 when recycle bin is disabled."""
        self._disable_recyclebin()
        response = self.api_session.delete("/@recyclebin")
        self.assertEqual(404, response.status_code)
        self.assertEqual("NotFound", response.json()["error"]["type"])

    def test_purge_item_disabled_recyclebin_returns_404(self):
        """DELETE /@recyclebin/{id} returns 404 when recycle bin is disabled."""
        self._disable_recyclebin()
        response = self.api_session.delete("/@recyclebin/some-id")
        self.assertEqual(404, response.status_code)


class TestRecycleBinRestore(RecycleBinTestBase):
    """Tests for POST /@recyclebin/{item_id}/restore."""

    def test_restore_item_returns_200(self):
        """POST /@recyclebin/{id}/restore returns 200 on success."""
        recycle_id, _title = self._add_document_to_recyclebin()
        response = self.api_session.post(f"/@recyclebin/{recycle_id}/restore")
        self.assertEqual(200, response.status_code)

    def test_restore_item_response_structure(self):
        """POST /@recyclebin/{id}/restore response contains status and restored_item."""
        recycle_id, _title = self._add_document_to_recyclebin()
        response = self.api_session.post(f"/@recyclebin/{recycle_id}/restore")
        data = response.json()
        self.assertEqual("success", data["status"])
        self.assertIn("message", data)
        self.assertIn("restored_item", data)

    def test_restore_item_restored_item_keys(self):
        """Restored item in response contains @id, id, title, @type."""
        recycle_id, _title = self._add_document_to_recyclebin(doc_title="Restored Doc")
        response = self.api_session.post(f"/@recyclebin/{recycle_id}/restore")
        restored = response.json()["restored_item"]
        self.assertIn("@id", restored)
        self.assertIn("id", restored)
        self.assertIn("title", restored)
        self.assertIn("@type", restored)

    def test_restore_item_title_matches(self):
        """Restored item title matches the original document title."""
        recycle_id, _title = self._add_document_to_recyclebin(
            doc_title="My Restored Doc"
        )
        response = self.api_session.post(f"/@recyclebin/{recycle_id}/restore")
        self.assertEqual("My Restored Doc", response.json()["restored_item"]["title"])

    def test_restore_item_appears_in_portal(self):
        """After restore, the document exists back in the portal."""
        recycle_id, _title = self._add_document_to_recyclebin(doc_id="restore-me")
        response = self.api_session.post(f"/@recyclebin/{recycle_id}/restore")
        self.assertEqual(200, response.status_code)
        restored_id = response.json()["restored_item"]["id"]
        transaction.abort()  # sync with what the WSGI request committed
        self.assertIn(restored_id, self.portal)

    def test_restore_removes_item_from_recyclebin(self):
        """After restore, the item is no longer in the recycle bin."""
        recycle_id, _title = self._add_document_to_recyclebin()
        self.api_session.post(f"/@recyclebin/{recycle_id}/restore")
        transaction.abort()  # sync with what the WSGI request committed
        recyclebin = getUtility(IRecycleBin)
        self.assertIsNone(recyclebin.get_item(recycle_id))

    def test_restore_nonexistent_item_returns_404(self):
        """POST /@recyclebin/{non-existent-id}/restore returns 404."""
        response = self.api_session.post("/@recyclebin/does-not-exist/restore")
        self.assertEqual(404, response.status_code)
        self.assertEqual("NotFound", response.json()["error"]["type"])

    def test_restore_with_invalid_action_returns_400(self):
        """POST /@recyclebin/{id}/not-restore returns 400 bad request."""
        recycle_id, _title = self._add_document_to_recyclebin()
        response = self.api_session.post(f"/@recyclebin/{recycle_id}/somethingelse")
        self.assertEqual(400, response.status_code)

    def test_restore_missing_action_segment_returns_400(self):
        """POST /@recyclebin/{id} (missing /restore) returns 400."""
        recycle_id, _title = self._add_document_to_recyclebin()
        response = self.api_session.post(f"/@recyclebin/{recycle_id}")
        self.assertEqual(400, response.status_code)

    def test_restore_to_different_target_path(self):
        """POST /@recyclebin/{id}/restore with target_path restores to given folder."""
        # Create a target folder (not deleted, so it stays in the portal)
        self.portal.invokeFactory("Folder", "target-folder", title="Target Folder")
        transaction.commit()

        recycle_id, _title = self._add_document_to_recyclebin(doc_id="doc-to-move")

        target_path = "/".join(self.portal["target-folder"].getPhysicalPath())
        # Strip the site root prefix and leading slash so it's a portal-relative path
        site_path = "/".join(self.portal.getPhysicalPath())
        relative_target = target_path[len(site_path) :].lstrip("/")

        response = self.api_session.post(
            f"/@recyclebin/{recycle_id}/restore",
            json={"target_path": relative_target},
        )
        self.assertEqual(200, response.status_code)
        restored_id = response.json()["restored_item"]["id"]
        transaction.abort()  # sync with what the WSGI request committed
        self.assertIn(restored_id, self.portal["target-folder"])

    def test_restore_disabled_recyclebin_returns_404(self):
        """POST /@recyclebin/{id}/restore returns 404 when recycle bin is disabled."""
        self._disable_recyclebin()
        response = self.api_session.post("/@recyclebin/some-id/restore")
        self.assertEqual(404, response.status_code)
        self.assertEqual("NotFound", response.json()["error"]["type"])


class TestRecycleBinPermissions(unittest.TestCase):
    """Tests that @recyclebin endpoints require cmf.ManagePortal permission.

    Anonymous users should get 401; authenticated users without ManagePortal
    should get 403.
    """

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # Enable recycle bin
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            IRecycleBinControlPanelSettings, prefix="recyclebin-controlpanel"
        )
        settings.recycling_enabled = True

        # Create a regular user without ManagePortal
        api.user.create(
            email="editor@example.com",
            username="editor-user",
            password=TEST_USER_PASSWORD,
        )

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    # ------------------------------------------------------------------
    # Anonymous (no credentials) → 401
    # ------------------------------------------------------------------

    def test_anonymous_get_listing_returns_401(self):
        """Anonymous cannot list the recycle bin."""
        anon_session = RelativeSession(self.portal_url, test=self)
        anon_session.headers.update({"Accept": "application/json"})
        response = anon_session.get("/@recyclebin")
        self.assertEqual(401, response.status_code)
        anon_session.close()

    def test_anonymous_get_item_returns_401(self):
        """Anonymous cannot retrieve a single recycle bin item."""
        anon_session = RelativeSession(self.portal_url, test=self)
        anon_session.headers.update({"Accept": "application/json"})
        response = anon_session.get("/@recyclebin/some-id")
        self.assertEqual(401, response.status_code)
        anon_session.close()

    def test_anonymous_purge_returns_401(self):
        """Anonymous cannot purge the recycle bin."""
        anon_session = RelativeSession(self.portal_url, test=self)
        anon_session.headers.update({"Accept": "application/json"})
        response = anon_session.delete("/@recyclebin")
        self.assertEqual(401, response.status_code)
        anon_session.close()

    def test_anonymous_restore_returns_401(self):
        """Anonymous cannot restore an item from the recycle bin."""
        anon_session = RelativeSession(self.portal_url, test=self)
        anon_session.headers.update({"Accept": "application/json"})
        response = anon_session.post("/@recyclebin/some-id/restore")
        self.assertEqual(401, response.status_code)
        anon_session.close()

    # ------------------------------------------------------------------
    # Regular editor (Member + Editor, no ManagePortal) → 401
    # Zope challenges with 401 even for authenticated users when the
    # permission check is handled purely by ZCML (no explicit code-level
    # Forbidden raise).
    # ------------------------------------------------------------------

    def test_editor_get_listing_returns_401(self):
        """Editor without ManagePortal gets 401 (Zope permission challenge)."""
        self.api_session.auth = ("editor-user", TEST_USER_PASSWORD)
        response = self.api_session.get("/@recyclebin")
        self.assertEqual(401, response.status_code)

    def test_editor_get_item_returns_401(self):
        """Editor without ManagePortal gets 401 on single item request."""
        self.api_session.auth = ("editor-user", TEST_USER_PASSWORD)
        response = self.api_session.get("/@recyclebin/some-id")
        self.assertEqual(401, response.status_code)

    def test_editor_purge_returns_401(self):
        """Editor without ManagePortal gets 401 on purge."""
        self.api_session.auth = ("editor-user", TEST_USER_PASSWORD)
        response = self.api_session.delete("/@recyclebin")
        self.assertEqual(401, response.status_code)

    def test_editor_restore_returns_401(self):
        """Editor without ManagePortal gets 401 on restore."""
        self.api_session.auth = ("editor-user", TEST_USER_PASSWORD)
        response = self.api_session.post("/@recyclebin/some-id/restore")
        self.assertEqual(401, response.status_code)
