# -*- coding: utf-8 -*-
from datetime import date
from decimal import Decimal
from unittest2 import TestCase

from zope.component import getMultiAdapter
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.app.textfield import RichText
from plone.autoform import directives as form
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.supermodel import model
from Products.CMFCore.utils import getToolByName

from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.restapi.types.utils import get_fields_from_schema
from plone.restapi.types.utils import get_jsonschema_for_fti
from plone.restapi.types.utils import get_jsonschema_for_portal_type


class IDummySchema(model.Schema):

    field1 = schema.Bool(
        title=u"Foo",
        description=u"",
    )

    field2 = schema.TextLine(
        title=u"Bar",
        description=u"",
    )

    form.mode(secret='hidden')
    secret = schema.TextLine(
        title=u"Secret",
        description=u"",
    )


class TestJsonSchemaUtils(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_get_fields_from_schema(self):
        fields = get_fields_from_schema(
            IDummySchema,
            self.portal,
            self.request
        )
        self.assertEqual(
            {
                'title': u'Foo',
                'description': u'',
                'type': 'boolean',
                'mode': u'input',
            },
            fields['field1'],
        )
        self.assertEqual(
            {
                'title': u'Bar',
                'description': u'',
                'type': 'string',
                'mode': u'input',
            },
            fields['field2']
        )
        self.assertEqual(
            {
                'title': u'Secret',
                'description': u'',
                'type': 'string',
                'mode': u'hidden',
            },
            fields['secret']
        )

    def test_get_jsonschema_for_fti(self):
        portal = self.portal
        request = self.request
        ttool = getToolByName(portal, 'portal_types')
        jsonschema = get_jsonschema_for_fti(
            ttool['Document'],
            portal, request
        )
        self.assertEqual(jsonschema['title'], 'Page')
        self.assertEqual(jsonschema['type'], 'object')
        self.assertIn('title', jsonschema['properties'].keys())
        self.assertIn('title', jsonschema['required'])
        self.assertEquals('default', jsonschema['fieldsets'][0]['id'])
        self.assertIn('title', jsonschema['fieldsets'][0]['fields'])

        jsonschema = get_jsonschema_for_fti(
            ttool['Document'],
            portal,
            request,
            excluded_fields=['title']
        )
        self.assertNotIn('title', jsonschema['properties'].keys())

    def test_get_jsonschema_for_portal_type(self):
        portal = self.portal
        request = self.request
        jsonschema = get_jsonschema_for_portal_type(
            'Document',
            portal,
            request
        )
        self.assertEqual(jsonschema['title'], 'Page')
        self.assertEqual(jsonschema['type'], 'object')
        self.assertIn('title', jsonschema['properties'].keys())
        self.assertIn('title', jsonschema['required'])
        self.assertEquals('default', jsonschema['fieldsets'][0]['id'])
        self.assertIn('title', jsonschema['fieldsets'][0]['fields'])

        jsonschema = get_jsonschema_for_portal_type(
            'Document',
            portal,
            request,
            excluded_fields=['title']
        )
        self.assertNotIn('title', jsonschema['properties'].keys())


class TestJsonSchemaProviders(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.dummy_vocabulary = SimpleVocabulary(
            [
                SimpleTerm(value=u'foo', title=u'Foo'),
                SimpleTerm(value=u'bar', title=u'Bar')
            ]
        )

    def test_textline(self):
        field = schema.TextLine(
            title=u'My field',
            description=u'My great field',
            default=u'foobar'
        )
        adapter = getMultiAdapter((field, self.portal, self.request),
                                  IJsonSchemaProvider)

        self.assertEqual(
            {
                'type': 'string',
                'title': u'My field',
                'description': u'My great field',
                'default': u'foobar',
            },
            adapter.get_schema()
        )

    def test_text(self):
        field = schema.Text(
            title=u'My field',
            description=u'My great field',
            default=u'Lorem ipsum dolor sit amet',
            min_length=10,
        )
        adapter = getMultiAdapter((field, self.portal, self.request),
                                  IJsonSchemaProvider)

        self.assertEqual(
            {
                'type': 'string',
                'title': u'My field',
                'description': u'My great field',
                'widget': 'textarea',
                'default': u'Lorem ipsum dolor sit amet',
                'minLength': 10,
            },
            adapter.get_schema()
        )

    def test_bool(self):
        field = schema.Bool(
            title=u'My field',
            description=u'My great field',
            default=False,
        )
        adapter = getMultiAdapter((field, self.portal, self.request),
                                  IJsonSchemaProvider)

        self.assertEqual(
            {
                'type': 'boolean',
                'title': u'My field',
                'description': u'My great field',
                'default': False,
            },
            adapter.get_schema()
        )

    def test_float(self):
        field = schema.Float(
            title=u'My field',
            description=u'My great field',
            min=0.0,
            max=1.0,
            default=0.5,
        )
        adapter = getMultiAdapter((field, self.portal, self.request),
                                  IJsonSchemaProvider)

        self.assertEqual(
            {
                'minimum': 0.0,
                'maximum': 1.0,
                'type': 'number',
                'title': u'My field',
                'description': u'My great field',
                'default': 0.5,
            },
            adapter.get_schema()
        )

    def test_decimal(self):
        field = schema.Decimal(
            title=u'My field',
            description=u'My great field',
            min=Decimal(0),
            max=Decimal(1),
            default=Decimal(0.5),
        )
        adapter = getMultiAdapter((field, self.portal, self.request),
                                  IJsonSchemaProvider)

        self.assertEqual(
            {
                'minimum': 0.0,
                'maximum': 1.0,
                'type': 'number',
                'title': u'My field',
                'description': u'My great field',
                'default': 0.5,
            },
            adapter.get_schema()
        )

    def test_int(self):
        field = schema.Int(
            title=u'My field',
            description=u'My great field',
            min=0,
            max=100,
            default=50,
        )
        adapter = getMultiAdapter((field, self.portal, self.request),
                                  IJsonSchemaProvider)

        self.assertEqual(
            {
                'minimum': 0,
                'maximum': 100,
                'type': 'integer',
                'title': u'My field',
                'description': u'My great field',
                'default': 50,
            },
            adapter.get_schema()
        )

    def test_choice(self):
        field = schema.Choice(
            title=u'My field',
            description=u'My great field',
            vocabulary=self.dummy_vocabulary,
        )
        adapter = getMultiAdapter((field, self.portal, self.request),
                                  IJsonSchemaProvider)

        self.assertEqual(
            {
                'type': 'string',
                'title': u'My field',
                'description': u'My great field',
                'enum': ['foo', 'bar'],
                'enumNames': ['Foo', 'Bar'],
                'choices': [('foo', 'Foo'), ('bar', 'Bar')],
            },
            adapter.get_schema()
        )

    def test_collection(self):
        field = schema.List(
            title=u'My field',
            description=u'My great field',
            min_length=1,
            value_type=schema.TextLine(
                title=u'Text',
                description=u'Text field',
                default=u'Default text'
            ),
            default=['foobar'],
        )
        adapter = getMultiAdapter((field, self.portal, self.request),
                                  IJsonSchemaProvider)

        self.assertEqual(
            {
                'type': 'array',
                'title': u'My field',
                'description': u'My great field',
                'default': ['foobar'],
                'minItems': 1,
                'uniqueItems': False,
                'additionalItems': True,
                'items': {
                    'type': 'string',
                    'title': u'Text',
                    'description': u'Text field',
                    'default': u'Default text',
                }
            },
            adapter.get_schema()
        )

        # Test Tuple
        field = schema.Tuple(
            title=u'My field',
            value_type=schema.Int(),
            default=(1, 2),
        )
        adapter = getMultiAdapter((field, self.portal, self.request),
                                  IJsonSchemaProvider)

        self.assertEqual(
            {
                'type': 'array',
                'title': u'My field',
                'description': u'',
                'uniqueItems': True,
                'additionalItems': True,
                'items': {
                    'title': u'',
                    'description': u'',
                    'type': 'integer',
                },
                'default': (1, 2),
            },
            adapter.get_schema()
        )

        # Test Set
        field = schema.Set(
            title=u'My field',
            value_type=schema.TextLine(),
        )
        adapter = getMultiAdapter((field, self.portal, self.request),
                                  IJsonSchemaProvider)

        self.assertEqual(
            {
                'type': 'array',
                'title': u'My field',
                'description': u'',
                'uniqueItems': True,
                'additionalItems': True,
                'items': {
                    'title': u'',
                    'description': u'',
                    'type': 'string',
                }
            },
            adapter.get_schema()
        )

        # List of choices
        field = schema.List(
            title=u'My field',
            value_type=schema.Choice(
                vocabulary=self.dummy_vocabulary,
            ),
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request),
            IJsonSchemaProvider
        )

        self.assertEqual(
            {
                'type': 'array',
                'title': u'My field',
                'description': u'',
                'uniqueItems': True,
                'additionalItems': True,
                'items': {
                    'title': u'',
                    'description': u'',
                    'type': 'string',
                    'enum': ['foo', 'bar'],
                    'enumNames': ['Foo', 'Bar'],
                    'choices': [('foo', 'Foo'), ('bar', 'Bar')],
                }
            },
            adapter.get_schema()
        )

    def test_object(self):
        field = schema.Object(
            title=u'My field',
            description=u'My great field',
            schema=IDummySchema,
        )
        adapter = getMultiAdapter((field, self.portal, self.request),
                                  IJsonSchemaProvider)
        jsonschema = adapter.get_schema()

        self.assertEqual(u'object', jsonschema['type'])
        self.assertEqual(u'My field', jsonschema['title'])
        self.assertEqual(u'My great field', jsonschema['description'])
        self.assertDictContainsSubset(
            {
                'field1': {
                    'title': u'Foo',
                    'description': u'',
                    'type': 'boolean',
                    'mode': u'input',
                },
            },
            jsonschema['properties']
        )
        self.assertDictContainsSubset(
            {
                'field2': {
                    'title': u'Bar',
                    'description': u'',
                    'type': 'string',
                    'mode': u'input',
                },
            },
            jsonschema['properties']
        )
        self.assertDictContainsSubset(
            {
                'secret': {
                    'title': u'Secret',
                    'description': u'',
                    'type': 'string',
                    'mode': u'hidden',
                },
            },
            jsonschema['properties']
        )

    def test_richtext(self):
        field = RichText(
            title=u'My field',
            description=u'My great field',
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request),
            IJsonSchemaProvider
        )

        self.assertEqual(
            {
                'type': 'string',
                'title': u'My field',
                'description': u'My great field',
                'widget': 'richtext',
            },
            adapter.get_schema()
        )

    def test_date(self):
        field = schema.Date(
            title=u'My field',
            description=u'My great field',
            default=date(2016, 1, 1),
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request),
            IJsonSchemaProvider
        )

        self.assertEqual(
            {
                'type': 'string',
                'title': u'My field',
                'description': u'My great field',
                'default': date(2016, 1, 1),
                'widget': u'date',
            },
            adapter.get_schema()
        )

    def test_datetime(self):
        field = schema.Datetime(
            title=u'My field',
            description=u'My great field',
        )
        adapter = getMultiAdapter(
            (field, self.portal, self.request),
            IJsonSchemaProvider
        )

        self.assertEqual(
            {
                'type': 'string',
                'title': u'My field',
                'description': u'My great field',
                'widget': u'datetime',
            },
            adapter.get_schema()
        )
