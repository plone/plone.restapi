# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces import IObjectEditedEvent
from Products.Archetypes.interfaces import IObjectInitializedEvent
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_AT_INTEGRATION_TESTING
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import provideHandler

import unittest


class TestATContentDeserializer(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

        self.doc1 = self.portal[self.portal.invokeFactory(
            'ATTestDocument', id='doc1', title='Test Document')]

    def deserialize(self, body='{}', validate_all=False):
        self.request['BODY'] = body
        deserializer = getMultiAdapter((self.doc1, self.request),
                                       IDeserializeFromJson)
        return deserializer(validate_all=validate_all)

    def test_deserializer_ignores_readonly_fields(self):
        self.doc1.getField('testReadonlyField').set(self.doc1, 'Readonly')
        self.deserialize(body='{"testReadonlyField": "Changed"}')
        self.assertEquals('Readonly', self.doc1.getTestReadonlyField())

    def test_deserializer_updates_field_value(self):
        self.deserialize(body='{"testStringField": "Updated"}')
        self.assertEquals('Updated', self.doc1.getTestStringField())

    def test_deserializer_validates_content(self):
        with self.assertRaises(BadRequest) as cm:
            self.deserialize(body='{"testURLField": "Not an URL"}')
        self.assertEquals(
            u"Validation failed(isURL): 'Not an URL' is not a valid url.",
            cm.exception.message[0]['message'])

    def test_deserializer_clears_creation_flag(self):
        self.doc1.markCreationFlag()
        self.deserialize(body='{"testStringField": "Updated"}')
        self.assertFalse(self.doc1.checkCreationFlag(),
                         'Creation flag not cleared')

    def test_deserializer_notifies_object_initialized(self):
        def handler(obj, event):
            obj._handler_called = True
        provideHandler(handler, (IBaseObject, IObjectInitializedEvent,))
        self.doc1.markCreationFlag()
        self.deserialize(body='{"testStringField": "Updated"}')
        self.assertTrue(getattr(self.doc1, '_handler_called', False),
                        'IObjectInitializedEvent not notified')

    def test_deserializer_notifies_object_edited(self):
        def handler(obj, event):
            obj._handler_called = True
        provideHandler(handler, (IBaseObject, IObjectEditedEvent,))
        self.doc1.unmarkCreationFlag()
        self.deserialize(body='{"testStringField": "Updated"}')
        self.assertTrue(getattr(self.doc1, '_handler_called', False),
                        'IObjectEditedEvent not notified')

    def test_deserializer_raises_if_required_value_is_missing(self):
        with self.assertRaises(BadRequest) as cm:
            self.deserialize(body='{"testStringField": "My Value"}',
                             validate_all=True)
        self.assertEquals(u'TestRequiredField is required, please correct.',
                          cm.exception.message[0]['message'])

    def test_deserializer_succeeds_if_required_value_is_provided(self):
        self.deserialize(body='{"testRequiredField": "My Value"}',
                         validate_all=True)
        self.assertEquals(u'My Value', self.portal.doc1.getTestRequiredField())
