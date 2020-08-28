# -*- coding: utf-8 -*-
from plone import api
from plone.browserlayer.utils import registered_layers
from plone.restapi import PROJECT_NAME
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:  # Plone < 5.1
    HAS_INSTALLER = False
else:
    HAS_INSTALLER = True


class TestInstall(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

    def test_product_is_installed(self):
        """Validate that our products GS profile has been run and the product
        installed
        """
        if HAS_INSTALLER:
            qi = get_installer(self.portal)
            installed = qi.is_product_installed(PROJECT_NAME)
        else:
            qi_tool = getToolByName(self.portal, "portal_quickinstaller")
            installed = PROJECT_NAME in [
                p["id"] for p in qi_tool.listInstalledProducts()
            ]
        self.assertTrue(installed, "package appears not to have been installed")


class TestUninstall(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

        if HAS_INSTALLER:
            qi = get_installer(self.portal)
            qi.uninstall_product(PROJECT_NAME)
            self.installed = qi.is_product_installed(PROJECT_NAME)
        else:
            qi_tool = getToolByName(self.portal, "portal_quickinstaller")
            with api.env.adopt_roles(["Manager"]):
                qi_tool.uninstallProducts(products=[PROJECT_NAME])
            self.installed = qi_tool.isProductInstalled(PROJECT_NAME)

    def test_uninstalled(self):
        self.assertFalse(self.installed)

    def test_addon_layer_removed(self):
        layers = [layer.getName() for layer in registered_layers()]
        self.assertNotIn("IPloneRestapiLayer", layers)
