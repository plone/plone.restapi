# -*- coding: utf-8 -*-
from datetime import date
from DateTime import DateTime
from plone import api
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from plone.restapi import HAS_AT
from plone.restapi.testing import PLONE_RESTAPI_AT_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.restapi.tests.helpers import result_paths
from plone.uuid.interfaces import IMutableUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.browser.overview import OverviewControlPanel
from zope.component import getUtility

import six
import transaction
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
        overview_control_panel = OverviewControlPanel(
            self.portal, self.request)
        self.core_versions = overview_control_panel.core_versions()

    def tearDown(self):
        self.api_session.close()

    def test_get_system(self):
        response = self.api_session.get("/@system")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get(
            "Content-Type"), "application/json")

        results = response.json()
        self.assertEqual(
            results[u"@id"],
            self.portal.absolute_url() + '/@system'
        )
        self.assertEqual(
            results["cmf_version"],
            self.core_versions.get("CMF")
        )
        self.assertEqual(
            results["debug-mode"],
            self.core_versions.get("Debug mode")
        )
        self.assertEqual(
            results["pil_version"],
            self.core_versions.get("PIL")
        )
        self.assertEqual(
            results["python_version"],
            self.core_versions.get("Python")
        )
        self.assertEqual(
            results["plone_gs_metadata_version_file_system"],
            self.core_versions.get("Plone File System")
        )
        self.assertEqual(
            results["plone_gs_metadata_version_installed"],
            self.core_versions.get("Plone Instance")
        )
        self.assertEqual(
            results["plone_version"],
            self.core_versions.get("Plone")
        )
        self.assertEqual(
            results["zope_version"],
            self.core_versions.get("Zope")
        )
