"""
Test Rest API endpoints for retrieving control panel system data.
"""

from plone.restapi import testing
from Products.CMFCore.utils import getToolByName

try:
    from Products.CMFPlone.controlpanel.browser.overview import OverviewControlPanel
except ImportError:
    from plone.app.controlpanel.overview import OverviewControlPanel


class TestSystemFunctional(testing.PloneRestAPIBrowserTestCase):
    """
    Test Rest API endpoints for retrieving control panel system data.
    """

    def setUp(self):
        """
        Capture useful references for testing against.
        """
        super().setUp()

        self.catalog = getToolByName(self.portal, "portal_catalog")

        overview_control_panel = OverviewControlPanel(self.portal, self.request)
        self.core_versions = overview_control_panel.core_versions()

    def test_get_system(self):
        response = self.api_session.get("/@system")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        results = response.json()
        self.assertEqual(results["@id"], self.portal.absolute_url() + "/@system")
        self.assertEqual(results["cmf_version"], self.core_versions.get("CMF"))
        self.assertEqual(results["debug_mode"], self.core_versions.get("Debug mode"))
        self.assertEqual(results["pil_version"], self.core_versions.get("PIL"))
        self.assertEqual(results["python_version"], self.core_versions.get("Python"))
        self.assertEqual(
            results["plone_gs_metadata_version_file_system"],
            self.core_versions.get("Plone File System"),
        )
        self.assertEqual(
            results["plone_gs_metadata_version_installed"],
            self.core_versions.get("Plone Instance"),
        )
        self.assertEqual(results["plone_version"], self.core_versions.get("Plone"))
        self.assertEqual(results["zope_version"], self.core_versions.get("Zope"))
