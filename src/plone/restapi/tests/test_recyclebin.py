from datetime import datetime
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession
from unittest import mock

import plone.restapi.testing
import transaction
import unittest


class TestRecycleBin(unittest.TestCase):
    layer = plone.restapi.testing.PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.api_session = RelativeSession(self.portal.absolute_url())
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        # For POST requests, set Content-Type header
        self.api_session.headers.update({"Content-Type": "application/json"})
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    # GET tests (from TestRecycleBinGet)
    def test_recyclebin_get_disabled(self):
        """Test GET /@recyclebin when recycle bin is disabled"""
        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = False

        with mock.patch(
            "plone.restapi.services.recyclebin.get.getUtility", return_value=recycle_bin
        ):
            response = self.api_session.get("/@recyclebin")

        self.assertEqual(404, response.status_code)
        self.assertEqual("NotFound", response.json()["error"]["type"])
        self.assertEqual("Recycle bin is disabled", response.json()["error"]["message"])

    def test_recyclebin_get_enabled_empty(self):
        """Test GET /@recyclebin when recycle bin is enabled but empty"""
        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = True
        recycle_bin.get_items.return_value = []

        with mock.patch(
            "plone.restapi.services.recyclebin.get.getUtility", return_value=recycle_bin
        ):
            response = self.api_session.get("/@recyclebin")

        self.assertEqual(200, response.status_code)
        result = response.json()
        self.assertEqual(self.portal.absolute_url() + "/@recyclebin", result["@id"])
        self.assertEqual(0, result["items_total"])
        self.assertEqual([], result["items"])

    def test_recyclebin_get_enabled_with_items(self):
        """Test GET /@recyclebin when recycle bin has items"""
        sample_date = datetime(2023, 1, 1, 12, 0, 0)
        mock_items = [
            {
                "id": "document1",
                "title": "Test Document",
                "type": "Document",
                "path": "/plone/document1",
                "parent_path": "/plone",
                "deletion_date": sample_date,
                "size": 1024,
                "recycle_id": "123456789",
            },
            {
                "id": "folder1",
                "title": "Test Folder",
                "type": "Folder",
                "path": "/plone/folder1",
                "parent_path": "/plone",
                "deletion_date": sample_date,
                "size": 512,
                "recycle_id": "987654321",
            },
        ]

        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = True
        recycle_bin.get_items.return_value = mock_items

        with mock.patch(
            "plone.restapi.services.recyclebin.get.getUtility", return_value=recycle_bin
        ):
            response = self.api_session.get("/@recyclebin")

        self.assertEqual(200, response.status_code)
        result = response.json()
        self.assertEqual(self.portal.absolute_url() + "/@recyclebin", result["@id"])
        self.assertEqual(2, result["items_total"])

        # Check first item
        item1 = result["items"][0]
        self.assertEqual("document1", item1["id"])
        self.assertEqual("Test Document", item1["title"])
        self.assertEqual("Document", item1["type"])
        self.assertEqual("/plone/document1", item1["path"])
        self.assertEqual("/plone", item1["parent_path"])
        self.assertEqual(sample_date.isoformat(), item1["deletion_date"])
        self.assertEqual(1024, item1["size"])
        self.assertEqual("123456789", item1["recycle_id"])
        self.assertEqual(
            self.portal.absolute_url() + "/@recyclebin/123456789", item1["@id"]
        )

        # Verify actions
        self.assertEqual(
            self.portal.absolute_url() + "/@recyclebin-restore",
            item1["actions"]["restore"],
        )
        self.assertEqual(
            self.portal.absolute_url() + "/@recyclebin-purge", item1["actions"]["purge"]
        )

    # RESTORE tests (from TestRecycleBinRestore)
    def test_restore_missing_item_id(self):
        """Test restore with missing item_id parameter"""
        response = self.api_session.post("/@recyclebin-restore", json={})

        self.assertEqual(400, response.status_code)
        self.assertEqual("BadRequest", response.json()["error"]["type"])
        self.assertEqual(
            "Missing required parameter: item_id", response.json()["error"]["message"]
        )

    def test_restore_disabled_recyclebin(self):
        """Test restore when recyclebin is disabled"""
        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = False

        with mock.patch(
            "plone.restapi.services.recyclebin.restore.getUtility",
            return_value=recycle_bin,
        ):
            response = self.api_session.post(
                "/@recyclebin-restore", json={"item_id": "123456789"}
            )

        self.assertEqual(404, response.status_code)
        self.assertEqual("NotFound", response.json()["error"]["type"])
        self.assertEqual("Recycle bin is disabled", response.json()["error"]["message"])

    def test_restore_nonexistent_item(self):
        """Test restore for a non-existent item"""
        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = True
        recycle_bin.get_item.return_value = None

        with mock.patch(
            "plone.restapi.services.recyclebin.restore.getUtility",
            return_value=recycle_bin,
        ):
            response = self.api_session.post(
                "/@recyclebin-restore", json={"item_id": "nonexistent"}
            )

        self.assertEqual(404, response.status_code)
        self.assertEqual("NotFound", response.json()["error"]["type"])
        self.assertEqual(
            "Item with ID nonexistent not found in recycle bin",
            response.json()["error"]["message"],
        )

    def test_restore_invalid_target_path(self):
        """Test restore with an invalid target path"""
        item_data = {
            "id": "document1",
            "title": "Test Document",
            "recycle_id": "123456789",
        }

        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = True
        recycle_bin.get_item.return_value = item_data

        with mock.patch(
            "plone.restapi.services.recyclebin.restore.getUtility",
            return_value=recycle_bin,
        ):
            response = self.api_session.post(
                "/@recyclebin-restore",
                json={"item_id": "123456789", "target_path": "/non/existent/path"},
            )

        self.assertEqual(400, response.status_code)
        self.assertEqual("BadRequest", response.json()["error"]["type"])
        self.assertEqual(
            "Target path /non/existent/path not found",
            response.json()["error"]["message"],
        )

    def test_restore_failure(self):
        """Test when restore operation fails"""
        item_data = {
            "id": "document1",
            "title": "Test Document",
            "recycle_id": "123456789",
        }

        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = True
        recycle_bin.get_item.return_value = item_data
        recycle_bin.restore_item.return_value = None

        with mock.patch(
            "plone.restapi.services.recyclebin.restore.getUtility",
            return_value=recycle_bin,
        ):
            response = self.api_session.post(
                "/@recyclebin-restore", json={"item_id": "123456789"}
            )

        self.assertEqual(500, response.status_code)
        self.assertEqual("InternalServerError", response.json()["error"]["type"])
        self.assertEqual("Failed to restore item", response.json()["error"]["message"])

    def test_restore_success(self):
        """Test successful item restoration"""
        item_data = {
            "id": "document1",
            "title": "Test Document",
            "recycle_id": "123456789",
        }

        # Mock restored object
        mock_obj = mock.Mock()
        mock_obj.absolute_url.return_value = "http://localhost:8080/plone/document1"
        mock_obj.getId.return_value = "document1"
        mock_obj.Title.return_value = "Test Document"
        mock_obj.portal_type = "Document"

        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = True
        recycle_bin.get_item.return_value = item_data
        recycle_bin.restore_item.return_value = mock_obj

        with mock.patch(
            "plone.restapi.services.recyclebin.restore.getUtility",
            return_value=recycle_bin,
        ):
            response = self.api_session.post(
                "/@recyclebin-restore", json={"item_id": "123456789"}
            )

        self.assertEqual(200, response.status_code)
        result = response.json()
        self.assertEqual("success", result["status"])
        self.assertEqual("Item document1 restored successfully", result["message"])

        # Verify restored item data
        restored = result["restored_item"]
        self.assertEqual("http://localhost:8080/plone/document1", restored["@id"])
        self.assertEqual("document1", restored["id"])
        self.assertEqual("Test Document", restored["title"])
        self.assertEqual("Document", restored["type"])

    # PURGE tests (from TestRecycleBinPurge)
    def test_purge_missing_parameters(self):
        """Test purge with missing parameters"""
        response = self.api_session.post("/@recyclebin-purge", json={})

        self.assertEqual(400, response.status_code)
        self.assertEqual("BadRequest", response.json()["error"]["type"])
        self.assertEqual(
            "Missing required parameter: item_id, purge_all, or purge_expired",
            response.json()["error"]["message"],
        )

    def test_purge_disabled_recyclebin(self):
        """Test purge when recyclebin is disabled"""
        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = False

        with mock.patch(
            "plone.restapi.services.recyclebin.purge.getUtility",
            return_value=recycle_bin,
        ):
            response = self.api_session.post(
                "/@recyclebin-purge", json={"item_id": "123456789"}
            )

        self.assertEqual(404, response.status_code)
        self.assertEqual("NotFound", response.json()["error"]["type"])
        self.assertEqual("Recycle bin is disabled", response.json()["error"]["message"])

    def test_purge_nonexistent_item(self):
        """Test purge for a non-existent item"""
        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = True
        recycle_bin.get_item.return_value = None

        with mock.patch(
            "plone.restapi.services.recyclebin.purge.getUtility",
            return_value=recycle_bin,
        ):
            response = self.api_session.post(
                "/@recyclebin-purge", json={"item_id": "nonexistent"}
            )

        self.assertEqual(404, response.status_code)
        self.assertEqual("NotFound", response.json()["error"]["type"])
        self.assertEqual(
            "Item with ID nonexistent not found in recycle bin",
            response.json()["error"]["message"],
        )

    def test_purge_failure(self):
        """Test when purge operation fails"""
        item_data = {
            "id": "document1",
            "title": "Test Document",
            "recycle_id": "123456789",
        }

        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = True
        recycle_bin.get_item.return_value = item_data
        recycle_bin.purge_item.return_value = False

        with mock.patch(
            "plone.restapi.services.recyclebin.purge.getUtility",
            return_value=recycle_bin,
        ):
            response = self.api_session.post(
                "/@recyclebin-purge", json={"item_id": "123456789"}
            )

        self.assertEqual(500, response.status_code)
        self.assertEqual("InternalServerError", response.json()["error"]["type"])
        self.assertEqual("Failed to purge item", response.json()["error"]["message"])

    def test_purge_success(self):
        """Test successful item purge"""
        item_data = {
            "id": "document1",
            "title": "Test Document",
            "recycle_id": "123456789",
        }

        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = True
        recycle_bin.get_item.return_value = item_data
        recycle_bin.purge_item.return_value = True

        with mock.patch(
            "plone.restapi.services.recyclebin.purge.getUtility",
            return_value=recycle_bin,
        ):
            response = self.api_session.post(
                "/@recyclebin-purge", json={"item_id": "123456789"}
            )

        self.assertEqual(200, response.status_code)
        result = response.json()
        self.assertEqual("success", result["status"])
        self.assertEqual("Item document1 purged successfully", result["message"])

    def test_purge_all(self):
        """Test purging all items"""
        mock_items = [
            {"id": "document1", "recycle_id": "123"},
            {"id": "document2", "recycle_id": "456"},
            {"id": "document3", "recycle_id": "789"},
        ]

        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = True
        recycle_bin.get_items.return_value = mock_items
        # Configure purge_item to return True for successful purge
        recycle_bin.purge_item.return_value = True

        with mock.patch(
            "plone.restapi.services.recyclebin.purge.getUtility",
            return_value=recycle_bin,
        ):
            response = self.api_session.post(
                "/@recyclebin-purge", json={"purge_all": True}
            )

        self.assertEqual(200, response.status_code)
        result = response.json()
        self.assertEqual("success", result["status"])
        self.assertEqual(3, result["purged_count"])
        self.assertEqual("Purged 3 items from recycle bin", result["message"])
        # Verify that purge_item was called for each item
        recycle_bin.purge_item.assert_any_call("123")
        recycle_bin.purge_item.assert_any_call("456")
        recycle_bin.purge_item.assert_any_call("789")

    def test_purge_expired(self):
        """Test purging expired items"""
        recycle_bin = mock.Mock()
        recycle_bin.is_enabled.return_value = True
        # Configure purge_expired_items to return the number of purged items
        recycle_bin.purge_expired_items.return_value = 2

        with mock.patch(
            "plone.restapi.services.recyclebin.purge.getUtility",
            return_value=recycle_bin,
        ):
            response = self.api_session.post(
                "/@recyclebin-purge", json={"purge_expired": True}
            )

        self.assertEqual(200, response.status_code)
        result = response.json()
        self.assertEqual("success", result["status"])
        self.assertEqual(2, result["purged_count"])
        self.assertEqual("Purged 2 expired items from recycle bin", result["message"])
