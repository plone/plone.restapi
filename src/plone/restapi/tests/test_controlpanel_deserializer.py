from plone.registry.interfaces import IRegistry
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zExceptions import BadRequest
from zope import schema
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import invariant
from zope.interface.exceptions import Invalid

import json
import unittest


class ILimits(Interface):
    lower = schema.Int(title="Lower", required=False)
    upper = schema.Int(title="Upper", required=False)


class IOrderedLimits(Interface):
    lower = schema.Int(title="Lower")
    upper = schema.Int(title="Upper")

    @invariant
    def ordered(data):
        if data.lower > data.upper:
            raise Invalid("Lower must not exceed upper")


class TestControlpanelDeserializer(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.registry = getUtility(IRegistry)
        for interface in (ILimits, IOrderedLimits):
            self.registry.registerInterface(interface, prefix=interface.__name__)

    def deserialize(self, interface, data):
        class Panel(RegistryConfigletPanel):
            schema = interface
            schema_prefix = interface.__name__
            configlet_id = "limits"
            configlet_category_id = "Products"

        self.request["BODY"] = json.dumps(data)
        IDeserializeFromJson(Panel(self.portal, self.request))()

    def stored(self, interface, name):
        return self.registry[f"{interface.__name__}.{name}"]

    def test_partial_update_keeps_omitted_fields(self):
        self.deserialize(ILimits, {"lower": 1, "upper": 10})
        self.deserialize(ILimits, {"lower": 5})
        self.assertEqual(self.stored(ILimits, "lower"), 5)
        self.assertEqual(self.stored(ILimits, "upper"), 10)

    def test_unknown_fields_are_ignored(self):
        self.deserialize(ILimits, {"lower": 2, "unknown": 1})
        self.assertEqual(self.stored(ILimits, "lower"), 2)

    def test_field_errors(self):
        with self.assertRaises(BadRequest) as raised:
            self.deserialize(ILimits, {"lower": "many"})
        self.assertEqual(
            raised.exception.args[0],
            [
                {
                    "field": "lower",
                    "message": "Invalid int literal.",
                    "error": "ValidationError",
                }
            ],
        )

    def test_invariant_errors_are_reported_once(self):
        with self.assertRaises(BadRequest) as raised:
            self.deserialize(IOrderedLimits, {"lower": 5, "upper": 1})
        self.assertEqual(
            raised.exception.args[0],
            [{"message": "Lower must not exceed upper", "error": "ValidationError"}],
        )

    def test_valid_values_pass_invariants(self):
        self.deserialize(IOrderedLimits, {"lower": 1, "upper": 5})
        self.assertEqual(self.stored(IOrderedLimits, "upper"), 5)
