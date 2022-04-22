"""
Test add-on installation.
"""

from plone.browserlayer.utils import registered_layers
from plone.restapi import PROJECT_NAME
from plone.restapi import testing
from Products.CMFPlone.utils import get_installer


class TestInstall(testing.PloneRestAPITestCase):
    """
    Test add-on installation.
    """

    def test_product_is_installed(self):
        """Validate that our products GS profile has been run and the product
        installed
        """
        qi = get_installer(self.portal)
        installed = qi.is_product_installed(PROJECT_NAME)
        self.assertTrue(installed, "package appears not to have been installed")


class TestUninstall(testing.PloneRestAPITestCase):
    """
    Test add-on uninstallation.
    """

    def setUp(self):
        """
        Uninstall this add-on to test against that state.
        """
        super().setUp()

        qi = get_installer(self.portal)
        qi.uninstall_product(PROJECT_NAME)
        self.installed = qi.is_product_installed(PROJECT_NAME)

    def test_uninstalled(self):
        self.assertFalse(self.installed)

    def test_addon_layer_removed(self):
        layers = [layer.getName() for layer in registered_layers()]
        self.assertNotIn("IPloneRestapiLayer", layers)
