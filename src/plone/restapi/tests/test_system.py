# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.CMFCore.utils import getToolByName

try:
    from Products.CMFPlone.controlpanel.browser.overview import OverviewControlPanel
except ImportError:
    from plone.app.controlpanel.overview import OverviewControlPanel

import unittest


class TestSystemFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST
        self.catalog = getToolByName(self.portal, "portal_catalog")

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        overview_control_panel = OverviewControlPanel(self.portal, self.request)
        self.core_versions = overview_control_panel.core_versions()

    def tearDown(self):
        self.api_session.close()

    def test_get_system(self):
        response = self.api_session.get("/@system")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        results = response.json()
        self.assertEqual(results[u"@id"], self.portal.absolute_url() + "/@system")
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
