from plone.browserlayer.utils import registered_layers
from plone.restapi import PROJECT_NAME
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING


try:
    from plone.base.utils import get_installer
except ImportError:
    # Plone 5.2
    from Products.CMFPlone.utils import get_installer

import unittest


class TestInstall(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

    def test_product_is_installed(self):
        """Validate that our products GS profile has been run and the product
        installed
        """
        qi = get_installer(self.portal)
        installed = qi.is_product_installed(PROJECT_NAME)
        self.assertTrue(installed, "package appears not to have been installed")


class TestUninstall(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

        qi = get_installer(self.portal)
        qi.uninstall_product(PROJECT_NAME)
        self.installed = qi.is_product_installed(PROJECT_NAME)

    def test_uninstalled(self):
        self.assertFalse(self.installed)

    def test_addon_layer_removed(self):
        layers = [layer.getName() for layer in registered_layers()]
        self.assertNotIn("IPloneRestapiLayer", layers)
