from plone.app.textfield import RichTextValue
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING

import unittest


class TestConverters(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def test_richtextvalue_converter(self):
        """test that a RichTextValue is converted to a proper JSON structure"""
        html = "<p>This is a demo HTML</p>"
        value = RichTextValue(html, "text/html", "text/html")
        json_compatible_value = json_compatible(value)
        self.assertEqual(
            json_compatible_value,
            {
                "data": html,
                "content-type": "text/html",
                "encoding": "utf-8",
            },
        )
