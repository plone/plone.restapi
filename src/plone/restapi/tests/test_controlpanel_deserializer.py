from plone.registry.interfaces import IRegistry
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zExceptions import BadRequest
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant

import json
import unittest


class IRangeSchema(Interface):
    low = schema.Int(title="Low", required=False)
    high = schema.Int(title="High", required=False)

    @invariant
    def low_below_high(data):
        if data.low is not None and data.high is not None and data.low > data.high:
            raise Invalid("Low must not be greater than high.")


class RangeControlpanel(RegistryConfigletPanel):
    schema = IRangeSchema
    schema_prefix = "plone.restapi.tests.range"


class TestControlpanelDeserializer(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.registry = getUtility(IRegistry)
        self.registry.registerInterface(
            IRangeSchema, prefix=RangeControlpanel.schema_prefix
        )
        self.proxy = self.registry.forInterface(
            IRangeSchema, prefix=RangeControlpanel.schema_prefix
        )
        self.proxy.low = 1
        self.proxy.high = 5

    def deserialize(self, body):
        self.request["BODY"] = json.dumps(body)
        controlpanel = RangeControlpanel(self.portal, self.request)
        deserializer = getMultiAdapter((controlpanel,), IDeserializeFromJson)
        return deserializer()

    def test_partial_update_satisfying_invariant_keeps_stored_values(self):
        self.deserialize({"low": 3})
        self.assertEqual(3, self.proxy.low)
        self.assertEqual(5, self.proxy.high)

    def test_partial_update_violating_invariant_against_stored_values(self):
        with self.assertRaises(BadRequest) as cm:
            self.deserialize({"low": 10})
        errors = cm.exception.args[0]
        self.assertEqual(1, len(errors))
        self.assertEqual("ValidationError", errors[0]["error"])
        self.assertEqual("Low must not be greater than high.", errors[0]["message"])
