# -*- coding: utf-8 -*-
from DateTime import DateTime
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.uuid.interfaces import IMutableUUID
from zope.component import getMultiAdapter

import json
import unittest


class TestDXContentSerializer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.portal.invokeFactory(
            'DXTestDocument',
            id=u'doc1',
            test_ascii_field='foo',
            test_asciiline_field='foo',
            test_bool_field=True,
            test_bytes_field='\xc3\xa4\xc3\xb6\xc3\xbc',
            test_bytesline_field='\xc3\xa4\xc3\xb6\xc3\xbc',
            test_choice_field=u'foo',
            test_date_field=date(2015, 7, 15),
            test_datetime_field=datetime(2015, 6, 20, 13, 22, 4),
            test_decimal_field='1.1',
            test_dict_field={'foo': 'bar', 'spam': 'eggs', '1': 1},
            test_float_field=1.5,
            test_frozenset_field=frozenset([1, 2, 3]),
            test_int_field=500,
            test_list_field=[1, 'two', 3],
            test_set_field=set(['a', 'b', 'c']),
            test_text_field=u'Käfer',
            test_textline_field=u'Käfer',
            test_time_field=time(14, 15, 33),
            test_timedelta_field=timedelta(44),
            test_tuple_field=(1, 1),
            test_readonly_field=u'readonly',
            test_read_permission_field=u'Secret Stuff')

        self.portal.doc1.creation_date = DateTime('2015-04-27T10:14:48+00:00')
        self.portal.doc1.modification_date = DateTime(
            '2015-04-27T10:24:11+00:00')
        IMutableUUID(self.portal.doc1).set('30314724b77a4ec0abbad03d262837aa')

    def serialize(self):
        serializer = getMultiAdapter((self.portal.doc1, self.request),
                                     ISerializeToJson)
        return serializer()

    def test_serializer_returns_json_serializeable_object(self):
        obj = self.serialize()
        self.assertTrue(isinstance(json.dumps(obj), str),
                        'Not JSON serializable')

    @unittest.skip('We do not include the context at this point')
    def test_serializer_includes_context(self):
        obj = self.serialize()
        self.assertIn(u'@context', obj)
        self.assertEqual(u'http://www.w3.org/ns/hydra/context.jsonld',
                         obj[u'@context'])

    def test_serializer_includes_json_ld_id(self):
        obj = self.serialize()
        self.assertIn(u'@id', obj)
        self.assertEqual(self.portal.doc1.absolute_url(), obj[u'@id'])

    def test_serializer_includes_id(self):
        obj = self.serialize()
        self.assertIn(u'id', obj)
        self.assertEqual(self.portal.doc1.id, obj[u'id'])

    def test_serializer_includes_type(self):
        obj = self.serialize()
        self.assertIn(u'@type', obj)
        self.assertEqual(self.portal.doc1.portal_type, obj[u'@type'])

    def test_serializer_includes_review_state(self):
        obj = self.serialize()
        self.assertIn(u'review_state', obj)
        self.assertEqual(u'private', obj[u'review_state'])

    def test_serializer_includes_uid(self):
        obj = self.serialize()
        self.assertIn(u'UID', obj)
        self.assertEqual(u'30314724b77a4ec0abbad03d262837aa', obj[u'UID'])

    def test_serializer_includes_creation_date(self):
        obj = self.serialize()
        self.assertIn(u'created', obj)
        self.assertEqual(u'2015-04-27T10:14:48+00:00', obj[u'created'])

    def test_serializer_includes_modification_date(self):
        obj = self.serialize()
        self.assertIn(u'modified', obj)
        self.assertEqual(u'2015-04-27T10:24:11+00:00', obj[u'modified'])

    def test_serializer_ignores_field_without_read_permission(self):
        self.portal.doc1.test_read_permission_field = u'Secret Stuff'
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertNotIn(u'test_read_permission_field', self.serialize())

    def test_serializer_includes_field_with_read_permission(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        obj = self.serialize()
        self.assertIn(u'test_read_permission_field', obj)
        self.assertEqual(u'Secret Stuff', obj[u'test_read_permission_field'])

    def test_get_layout(self):
        current_layout = self.portal.doc1.getLayout()
        obj = self.serialize()
        self.assertIn('layout', obj)
        self.assertEquals(current_layout, obj['layout'])
