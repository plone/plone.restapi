from plone.restapi.deserializer import boolean_value
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING

import unittest


class TestBooleanValue(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def test_boolean_value_true_bool(self):
        self.assertTrue(boolean_value(True))

    def test_boolean_value_true_string(self):
        self.assertTrue(boolean_value("true"))

    def test_boolean_value_true_string_uppercase(self):
        self.assertTrue(boolean_value("True"))

    def test_boolean_value_true_int(self):
        self.assertTrue(boolean_value(1))

    def test_boolean_value_true_int_string(self):
        self.assertTrue(boolean_value("1"))

    def test_boolean_value_yes(self):
        self.assertTrue(boolean_value("yes"))

    def test_boolean_value_on(self):
        self.assertTrue(boolean_value("on"))

    def test_boolean_value_false_bool(self):
        self.assertFalse(boolean_value(False))

    def test_boolean_value_false_string(self):
        self.assertFalse(boolean_value("false"))

    def test_boolean_value_false_string_uppercase(self):
        self.assertFalse(boolean_value("False"))

    def test_boolean_value_false_int(self):
        self.assertFalse(boolean_value(0))

    def test_boolean_value_false_int_string(self):
        self.assertFalse(boolean_value("0"))

    def test_boolean_value_no(self):
        self.assertFalse(boolean_value("no"))

    def test_boolean_value_off(self):
        self.assertFalse(boolean_value("off"))

    def test_boolean_value_false_for_unknown(self):
        self.assertFalse(boolean_value("foobar"))

    def test_boolean_value_strict_raises_for_unknown(self):
        with self.assertRaises(ValueError):
            boolean_value("foobar", strict=True)
