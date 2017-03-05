# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.restapi.testing import \
    PLONE_RESTAPI_DX_INTEGRATION_TESTING
import plone.api.portal


class TestExample(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = plone.api.portal.get_tool('portal_quickinstaller')

    def test_product_is_installed(self):
        """ Validate that our products GS profile has been run and the product
            installed
        """
        pid = 'plone.restapi'
        installed = [p['id'] for p in self.qi_tool.listInstalledProducts()]
        self.assertTrue(pid in installed,
                        'package appears not to have been installed')
