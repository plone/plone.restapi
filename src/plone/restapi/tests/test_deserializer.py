# -*- coding: utf-8 -*-
from plone.dexterity.fti import DexterityFTI
from plone.restapi.deserializer import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_INTEGRATION_TESTING
from zope.component import getMultiAdapter
import unittest


class TestDeserializeFromJson(unittest.TestCase):

    layer = PLONE_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        model_source = """
        <model xmlns="http://namespaces.plone.org/supermodel/schema">
          <schema>
            <field name="title" type="zope.schema.TextLine">
              <title>Title</title>
            </field>
            <field name="ro" type="zope.schema.TextLine">
              <title>Read-Only Field</title>
              <readonly>True</readonly>
            </field>
          </schema>
        </model>"""
        item_fti = DexterityFTI('Item', model_source=model_source)
        self.portal.portal_types._setObject('Item', item_fti)
        self.portal.invokeFactory(
            'Item', id='item1', title='Item 1', ro='readonly')

    def deserialize(self, set_default_values=False):
        deserializer = getMultiAdapter((self.portal.item1, self.request),
                                       IDeserializeFromJson)
        return deserializer()

    def test_deserializer_raises_with_invalid_body(self):
        self.request['BODY'] = 'Not a JSON object'
        with self.assertRaises(DeserializationError) as cm:
            self.deserialize()
        self.assertEquals('No JSON object could be decoded', cm.exception.msg)

    def test_deserializer_raises_with_malformed_body(self):
        self.request['BODY'] = '[1,2,3]'
        with self.assertRaises(DeserializationError) as cm:
            self.deserialize()
        self.assertEquals('Malformed body', cm.exception.msg)

    def test_deserializer_updates_field_value(self):
        self.request['BODY'] = '{"title": "My Item"}'
        self.deserialize()
        self.assertEquals(u'My Item', self.portal.item1.title)

    def test_deserializer_ignores_readonly_fields(self):
        self.request['BODY'] = '{"ro": "Foo"}'
        self.deserialize()
        self.assertEquals(u'readonly', self.portal.item1.ro)
