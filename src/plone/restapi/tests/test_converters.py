# -*- coding: utf-8 -*-

import unittest
from plone.app.textfield import RichTextValue
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING


class TestConverters(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def test_richtextvalue_converter(self):
        """test that a RichTextValue is converted to a proper HTML"""
        html = "<p>This is a demo HTML</p>"
        value = RichTextValue(html, "text/html", "text/html")
        json_compatible_value = IJsonCompatible(value)
        self.assertEqual(json_compatible_value, html)
