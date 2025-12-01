from plone.restapi.deserializer import boolean_value
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

import unittest


class TestBooleanValue(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def test_true_bool(self):
        self.assertTrue(boolean_value(True))

    def test_true_string(self):
        self.assertTrue(boolean_value("true"))

    def test_true_string_uppercase(self):
        self.assertTrue(boolean_value("True"))

    def test_true_int(self):
        self.assertTrue(boolean_value(1))

    def test_true_int_string(self):
        self.assertTrue(boolean_value("1"))

    def test_false_bool(self):
        self.assertFalse(boolean_value(False))

    def test_false_string(self):
        self.assertFalse(boolean_value("false"))

    def test_false_string_uppercase(self):
        self.assertFalse(boolean_value("False"))

    def test_false_int(self):
        self.assertFalse(boolean_value(0))

    def test_false_int_string(self):
        self.assertFalse(boolean_value("0"))

    def test_true_other_value(self):
        self.assertTrue(boolean_value("foobar"))
