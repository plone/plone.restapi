# -*- coding: utf-8 -*-
import unittest

from Products.CMFCore.utils import getToolByName
from plone.browserlayer.utils import registered_layers

from plone import api
from plone.restapi import PROJECT_NAME
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING


class TestInstall(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(PROJECT_NAME in installed,
                        'package appears not to have been installed')


class TestUninstall(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

        with api.env.adopt_roles(['Manager']):
            self.qi_tool.uninstallProducts(products=[PROJECT_NAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi_tool.isProductInstalled(PROJECT_NAME))

    def test_addon_layer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('IPloneRestapiLayer', layers)
