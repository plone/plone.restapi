import io
import os
import unittest

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession


THEMING_ZIPFILES = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "..",
    "..",
    "..",
    ".venv",
    "lib",
    "python3.12",
    "site-packages",
    "plone",
    "app",
    "theming",
    "tests",
    "zipfiles",
)

# Use a zip with a manifest so extractThemeInfo works
MANIFEST_ZIP = os.path.join(THEMING_ZIPFILES, "manifest_rules.zip")


def get_theming_zipfile(name):
    """Return the path to a plone.app.theming test zip file."""
    import plone.app.theming.tests

    tests_dir = os.path.dirname(plone.app.theming.tests.__file__)
    return os.path.join(tests_dir, "zipfiles", name)


class TestServicesThemes(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})

    def tearDown(self):
        self.api_session.close()

    def test_get_themes_list(self):
        response = self.api_session.get("/@themes")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        # Each theme should have basic fields
        theme = data[0]
        self.assertIn("id", theme)
        self.assertIn("title", theme)
        self.assertIn("active", theme)
        self.assertIn("@id", theme)

    def test_get_theme_by_name(self):
        # First get list to find a valid theme name
        response = self.api_session.get("/@themes")
        themes = response.json()
        theme_id = themes[0]["id"]

        response = self.api_session.get(f"/@themes/{theme_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], theme_id)

    def test_get_theme_not_found(self):
        response = self.api_session.get("/@themes/nonexistent-theme-xyz")
        self.assertEqual(response.status_code, 404)

    def test_post_theme_upload(self):
        zip_path = get_theming_zipfile("manifest_rules.zip")
        if not os.path.exists(zip_path):
            self.skipTest("plone.app.theming test zips not available")

        with open(zip_path, "rb") as f:
            response = self.api_session.post(
                "/@themes",
                files={"themeArchive": ("manifest_rules.zip", f, "application/zip")},
            )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("title", data)
        self.assertIn("@id", data)

    def test_post_theme_missing_archive(self):
        response = self.api_session.post(
            "/@themes",
            data={},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_post_theme_invalid_zip(self):
        fake_zip = io.BytesIO(b"not a zip file")
        response = self.api_session.post(
            "/@themes",
            files={"themeArchive": ("bad.zip", fake_zip, "application/zip")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_post_theme_duplicate_without_replace(self):
        zip_path = get_theming_zipfile("manifest_rules.zip")
        if not os.path.exists(zip_path):
            self.skipTest("plone.app.theming test zips not available")

        # Upload once
        with open(zip_path, "rb") as f:
            self.api_session.post(
                "/@themes",
                files={"themeArchive": ("manifest_rules.zip", f, "application/zip")},
            )

        # Upload again without replace
        with open(zip_path, "rb") as f:
            response = self.api_session.post(
                "/@themes",
                files={"themeArchive": ("manifest_rules.zip", f, "application/zip")},
            )

        self.assertEqual(response.status_code, 409)
        self.assertIn("error", response.json())

    def test_post_theme_duplicate_with_replace(self):
        zip_path = get_theming_zipfile("manifest_rules.zip")
        if not os.path.exists(zip_path):
            self.skipTest("plone.app.theming test zips not available")

        # Upload once
        with open(zip_path, "rb") as f:
            self.api_session.post(
                "/@themes",
                files={"themeArchive": ("manifest_rules.zip", f, "application/zip")},
            )

        # Upload again with replace=true
        with open(zip_path, "rb") as f:
            response = self.api_session.post(
                "/@themes",
                files={
                    "themeArchive": ("manifest_rules.zip", f, "application/zip"),
                },
                data={"replace": "true"},
            )

        self.assertEqual(response.status_code, 201)

    def test_patch_theme_activate(self):
        # Get a theme name from the list
        response = self.api_session.get("/@themes")
        themes = response.json()
        theme_id = themes[0]["id"]

        response = self.api_session.patch(
            f"/@themes/{theme_id}",
            json={"active": True},
        )
        self.assertEqual(response.status_code, 204)

    def test_patch_theme_deactivate(self):
        # Get a theme name from the list
        response = self.api_session.get("/@themes")
        themes = response.json()
        theme_id = themes[0]["id"]

        # Activate first
        self.api_session.patch(
            f"/@themes/{theme_id}",
            json={"active": True},
        )

        # Then deactivate
        response = self.api_session.patch(
            f"/@themes/{theme_id}",
            json={"active": False},
        )
        self.assertEqual(response.status_code, 204)

    def test_patch_theme_not_found(self):
        response = self.api_session.patch(
            "/@themes/nonexistent-theme-xyz",
            json={"active": True},
        )
        self.assertEqual(response.status_code, 404)

    def test_patch_theme_no_name(self):
        response = self.api_session.patch(
            "/@themes",
            json={"active": True},
        )
        self.assertEqual(response.status_code, 400)

    def test_patch_theme_invalid_body(self):
        response = self.api_session.get("/@themes")
        themes = response.json()
        theme_id = themes[0]["id"]

        response = self.api_session.patch(
            f"/@themes/{theme_id}",
            json={"active": "maybe"},
        )
        self.assertEqual(response.status_code, 400)
