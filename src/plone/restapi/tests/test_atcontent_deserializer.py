# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces import IObjectEditedEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.component import provideHandler

import unittest


class TestATContentDeserializer(unittest.TestCase):

    layer = PLONE_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.doc1 = self.portal[self.portal.invokeFactory(
            'ATTestDocument', id='doc1', title='Test Document')]

    def deserialize(self, set_default_values=False):
        deserializer = getMultiAdapter((self.doc1, self.request),
                                       IDeserializeFromJson)
        return deserializer()

    def test_deserializer_ignores_readonly_fields(self):
        self.doc1.getField('testReadonlyField').set(self.doc1, 'Readonly')
        self.request['BODY'] = '{"testReadonlyField": "Changed"}'
        self.deserialize()
        self.assertEquals('Readonly', self.doc1.getTestReadonlyField())

    def test_deserializer_updates_field_value(self):
        self.request['BODY'] = '{"testStringField": "Updated"}'
        self.deserialize()
        self.assertEquals('Updated', self.doc1.getTestStringField())

    def test_deserializer_validates_content(self):
        self.request['BODY'] = '{"testURLField": "Not an URL"}'
        with self.assertRaises(ValueError) as cm:
            self.deserialize()
        self.assertEquals(
            u"Validation failed(isURL): 'Not an URL' is not a valid url.",
            cm.exception.message['testURLField'])

    def test_deserializer_clears_creation_flag(self):
        self.request['BODY'] = '{"testStringField": "Updated"}'
        self.doc1.markCreationFlag()
        self.deserialize()
        self.assertFalse(self.doc1.checkCreationFlag(),
                         'Creation flag not cleared')

    def test_deserializer_notifies_object_initialized(self):
        def handler(obj, event):
            obj._handler_called = True
        provideHandler(handler, (IBaseObject, IObjectInitializedEvent,))
        self.request['BODY'] = '{"testStringField": "Updated"}'
        self.doc1.markCreationFlag()
        self.deserialize()
        self.assertTrue(getattr(self.doc1, '_handler_called', False),
                        'IObjectInitializedEvent not notified')

    def test_deserializer_notifies_object_edited(self):
        def handler(obj, event):
            obj._handler_called = True
        provideHandler(handler, (IBaseObject, IObjectEditedEvent,))
        self.request['BODY'] = '{"testStringField": "Updated"}'
        self.doc1.unmarkCreationFlag()
        self.deserialize()
        self.assertTrue(getattr(self.doc1, '_handler_called', False),
                        'IObjectEditedEvent not notified')
