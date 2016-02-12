# -*- coding: utf-8 -*-
from DateTime import DateTime
from datetime import date
from datetime import datetime
from datetime import time
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.uuid.interfaces import IMutableUUID
from zope.component import getMultiAdapter
# from datetime import timedelta

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
            # test_frozenset_field=frozenset([1, 2, 3]),
            test_int_field=500,
            test_list_field=[1, 'two', 3],
            # test_set_field=set(['a', 'b', 'c']),
            test_text_field=u'Käfer',
            test_textline_field=u'Käfer',
            test_time_field=time(14, 15, 33),
            # test_timedelta_field=timedelta(44),
            test_tuple_field=(1, 1),
            test_readonly_field=u'readonly')

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
        self.assertDictEqual({
            u'@context': u'http://www.w3.org/ns/hydra/context.jsonld',
            u'@id': u'http://nohost/plone/doc1',
            u'@type': u'DXTestDocument',
            u'UID': u'30314724b77a4ec0abbad03d262837aa',
            u'created': u'2015-04-27T10:14:48+00:00',
            u'modified': u'2015-04-27T10:24:11+00:00',
            u'parent': {u'@id': u'http://nohost/plone',
                        u'description': u'',
                        u'title': u'Plone site'},
            u'test_annotations_behavior_field': None,
            u'test_ascii_field': u'foo',
            u'test_asciiline_field': u'foo',
            u'test_behavior_field': None,
            u'test_bool_field': True,
            u'test_bytes_field': u'\xe4\xf6\xfc',
            u'test_bytesline_field': u'\xe4\xf6\xfc',
            u'test_choice_field': u'foo',
            u'test_constraint_field': None,
            u'test_date_field': u'2015-07-15',
            u'test_datetime_field': u'2015-06-20T13:22:04',
            u'test_datetime_min_field': None,
            u'test_decimal_field': u'1.1',
            u'test_default_factory_field': u'DefaultFactory',
            u'test_default_value_field': u'Default',
            u'test_dict_field': {u'1': 1, u'foo': u'bar', u'spam': u'eggs'},
            u'test_dict_key_type_field': None,
            u'test_float_field': 1.5,
            u'test_frozenset_field': None,
            u'test_int_field': 500,
            u'test_invariant_field1': None,
            u'test_invariant_field2': None,
            u'test_list_field': [1, u'two', 3],
            u'test_list_value_type_field': None,
            u'test_maxlength_field': None,
            u'test_namedblobfile_field': u'http://nohost/plone/doc1/@@download'
            '/test_namedblobfile_field',
            u'test_namedblobimage_field': {
                u'icon': u'http://nohost/plone/doc1/@@images/image/icon',
                u'large': u'http://nohost/plone/doc1/@@images/image/large',
                u'listing': u'http://nohost/plone/doc1/@@images/image/listing',
                u'mini': u'http://nohost/plone/doc1/@@images/image/mini',
                u'original': u'http://nohost/plone/doc1/@@images/test_namedblo'
                'bimage_field',
                u'preview': u'http://nohost/plone/doc1/@@images/image/preview',
                u'thumb': u'http://nohost/plone/doc1/@@images/image/thumb',
                u'tile': u'http://nohost/plone/doc1/@@images/image/tile'},
            u'test_namedfile_field': u'http://nohost/plone/doc1/@@download/tes'
            't_namedfile_field',
            u'test_namedimage_field': {
                u'icon': u'http://nohost/plone/doc1/@@images/image/icon',
                u'large': u'http://nohost/plone/doc1/@@images/image/large',
                u'listing': u'http://nohost/plone/doc1/@@images/image/listing',
                u'mini': u'http://nohost/plone/doc1/@@images/image/mini',
                u'original': u'http://nohost/plone/doc1/@@images/test_namedima'
                'ge_field',
                u'preview': u'http://nohost/plone/doc1/@@images/image/preview',
                u'thumb': u'http://nohost/plone/doc1/@@images/image/thumb',
                u'tile': u'http://nohost/plone/doc1/@@images/image/tile'},
            u'test_nested_dict_field': None,
            u'test_nested_list_field': None,
            u'test_read_permission_field': None,
            u'test_readonly_field': u'readonly',
            u'test_relationchoice_field': None,
            u'test_relationlist_field': None,
            u'test_required_field': None,
            u'test_richtext_field': None,
            u'test_set_field': None,
            u'test_text_field': u'K\xe4fer',
            u'test_textline_field': u'K\xe4fer',
            u'test_time_field': u'14:15:33',
            u'test_time_min_field': None,
            u'test_timedelta_field': None,
            u'test_timedelta_min_field': None,
            u'test_tuple_field': [1, 1],
            u'test_write_permission_field': None},
            obj)
        self.assertTrue(isinstance(json.dumps(obj), str),
                        'Not JSON serializable')

    def test_serializer_ignores_field_without_read_permission(self):
        self.portal.doc1.test_read_permission_field = u'Secret Stuff'
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertNotIn(u'test_read_permission_field', self.serialize())
