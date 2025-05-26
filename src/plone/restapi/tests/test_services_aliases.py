from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestAliases(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.portal.invokeFactory("Document", id="front-page")
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_alias_non_root(self):
        data = {
            "items": [
                {
                    "path": "/alias-with-date",
                    "redirect-to": "/front-page",
                    "datetime": "2024-09-17T12:00:00",
                }
            ]
        }
        response = self.api_session.post("/front-page/@aliases", json=data)
        self.assertEqual(response.status_code, 204)

        # Verify alias exists
        response = self.api_session.get("/front-page/@aliases")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_alias_add_invalid_datetime(self):
        """Test POST /@aliases with an invalid datetime, makes invalid date=None"""
        data = {
            "items": [
                {
                    "path": "/alias-with-valid-date",
                    "redirect-to": "/front-page",
                    "datetime": "2024-09-17T12:00:00",
                },
                {
                    "path": "/alias-with-invalid-date",
                    "redirect-to": "/front-page",
                    "datetime": "invalid-date",
                },
            ]
        }
        response = self.api_session.post("/@aliases", json=data)
        self.assertEqual(response.status_code, 204)
        response = self.api_session.get("/@aliases")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 2)

    def test_alias_add_invalid_path(self):
        """Test POST /@aliases with an invalid path"""

        data = {"items": [{"path": "/valid-path", "redirect-to": "invalid-redirect"}]}
        response = self.api_session.post("/@aliases", json=data)
        self.assertEqual(response.status_code, 400)
        response = self.api_session.get("/@aliases")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 0)

    def test_duplicate_alias(self):
        data = {
            "items": [
                {"path": "/duplicate-alias", "redirect-to": "/front-page"},
                {"path": "/duplicate-alias", "redirect-to": "/front-page"},
            ]
        }
        self.api_session.post("/@aliases", json=data)
        response = self.api_session.post("/@aliases", json=data)
        self.assertEqual(response.status_code, 400)

    def test_alias_without_redirect(self):
        data = {"items": [{"path": "/alias-without-redirect"}]}
        response = self.api_session.post("/@aliases", json=data)
        self.assertEqual(response.status_code, 400)

    def test_alias_csv_upload(self):
        """Test POST /@aliases for CSV upload"""

        content = b"old path,new path,datetime,manual\n/old-page,/front-page,2022/01/01 00:00:00 GMT+0,True\n"

        response = self.api_session.post(
            "/@aliases",
            files={"file": ("aliases.csv", content, "text/csv")},
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        response = self.api_session.get("/@aliases")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json().get("items"),
            [
                {
                    "datetime": "2022-01-01T00:00:00+00:00",
                    "manual": True,
                    "path": "/old-page",
                    "redirect-to": "/front-page",
                }
            ],
        )

    def test_alias_csv_download(self):
        """Test GET /@aliases with CSV output"""

        data = {
            "items": [
                {
                    "path": "/alias-page",
                    "redirect-to": "/front-page",
                    "datetime": "2022/01/01 00:00:00 GMT+0",
                },
            ]
        }
        self.api_session.post("/@aliases", json=data)
        headers = {"Accept": "text/csv"}
        response = self.api_session.get("/@aliases", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Content-Disposition", response.headers)
        self.assertEqual(response.headers["Content-Type"], "text/csv; charset=utf-8")
        content = b"old path,new path,datetime,manual\r\n/alias-page,/front-page,2022/01/01 00:00:00 GMT+0,True\r\n"
        self.assertEqual(content, response.content)

    def test_alias_delete(self):
        data = {"items": [{"path": "/alias-to-delete", "redirect-to": "/front-page"}]}
        self.api_session.post("/@aliases", json=data)
        response = self.api_session.delete(
            "/@aliases",
            json={
                "items": [
                    {
                        "path": "/alias-to-delete",
                    }
                ]
            },
        )
        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/@aliases")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 0)
