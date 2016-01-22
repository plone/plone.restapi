# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityItem
from plone.restapi.deserializer import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.testing import PLONE_RESTAPI_INTEGRATION_TESTING
from plone.restapi.tests.dxtypes import ITestAnnotationsBehavior
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import provideHandler
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

import unittest


class TestDXContentDeserializer(unittest.TestCase):

    layer = PLONE_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.portal.invokeFactory(
            'DXTestDocument',
            id=u'doc1',
            test_textline_field=u'Test Document',
            test_readonly_field=u'readonly')

    def deserialize(self, body='{}'):
        self.request['BODY'] = body
        deserializer = getMultiAdapter((self.portal.doc1, self.request),
                                       IDeserializeFromJson)
        return deserializer()

    def test_deserializer_raises_with_invalid_body(self):
        with self.assertRaises(DeserializationError) as cm:
            self.deserialize(body='Not a JSON object')
        self.assertEquals('No JSON object could be decoded', cm.exception.msg)

    def test_deserializer_raises_with_malformed_body(self):
        with self.assertRaises(DeserializationError) as cm:
            self.deserialize(body='[1,2,3]')
        self.assertEquals('Malformed body', cm.exception.msg)

    def test_deserializer_updates_field_value(self):
        self.deserialize(body='{"test_textline_field": "My Item"}')
        self.assertEquals(u'My Item', self.portal.doc1.test_textline_field)

    def test_deserializer_ignores_readonly_fields(self):
        self.deserialize(body='{"test_readonly_field": "Foo"}')
        self.assertEquals(u'readonly', self.portal.doc1.test_readonly_field)

    def test_deserializer_notifies_object_modified(self):
        def handler(obj, event):
            obj._handler_called = True
        provideHandler(handler, (IDexterityItem, IObjectModifiedEvent,))
        self.deserialize(body='{"test_textline_field": "My Item"}')
        self.assertTrue(getattr(self.portal.doc1, '_handler_called', False),
                        'IObjectEditedEvent not notified')

    def test_deserializer_does_not_update_field_without_write_permission(self):
        self.portal.doc1.test_write_permission_field = u'Test Write Permission'
        setRoles(self.portal,
                 TEST_USER_ID, ['Member', 'Contributor', 'Editor'])
        self.deserialize(body='{"test_write_permission_field": "Foo"}')
        self.assertEquals(u'Test Write Permission',
                          self.portal.doc1.test_write_permission_field)

    def test_deserializer_updates_field_with_write_permission(self):
        self.portal.doc1.test_write_permission_field = u'Test Write Permission'
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])
        self.deserialize(body='{"test_write_permission_field": "Foo"}')
        self.assertEquals(u'Foo',
                          self.portal.doc1.test_write_permission_field)

    def test_deserializer_validates_invariant(self):
        with self.assertRaises(BadRequest) as cm:
            self.deserialize(body='{"test_invariant_field1": "Foo",'
                                  ' "test_invariant_field2": "Bar"}')
        self.assertEquals(u'Must have same values',
                          cm.exception.message[0]['message'])

    def test_deserializer_updates_behavior_field_value(self):
        self.deserialize(body='{"test_behavior_field": "My Value"}')
        self.assertEquals(u'My Value', self.portal.doc1.test_behavior_field)

    def test_deserializer_updates_behavior_field_value_in_annotations(self):
        self.deserialize(
            body='{"test_annotations_behavior_field": "My Value"}')
        self.assertEquals(
            u'My Value',
            ITestAnnotationsBehavior(self.portal.doc1)
            .test_annotations_behavior_field)
