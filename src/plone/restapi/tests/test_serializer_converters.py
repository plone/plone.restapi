# -*- coding: utf-8 -*-
from datetime import date
from DateTime import DateTime
from datetime import time
from datetime import timedelta
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from unittest import TestCase
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.intid.interfaces import IIntIds

import json
import Missing


class TestJsonCompatibleConverters(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def test_None(self):
        self.assertEquals(None, json_compatible(None))
        self.assertEquals('null', json.dumps(json_compatible(None)))

    def test_error_when_type_unknown(self):
        err_regex = r'^No converter for making <object object at [^>]*>' + \
                    r' \(<type \'object\'>\) JSON compatible.$'

        with self.assertRaisesRegexp(TypeError, err_regex):
            json_compatible(object())

        with self.assertRaisesRegexp(TypeError, err_regex):
            json_compatible({'foo': [object()]})

    def test_True(self):
        self.assertEquals(True, json_compatible(True))
        self.assertEquals('true', json.dumps(json_compatible(True)))

    def test_False(self):
        self.assertEquals(False, json_compatible(False))
        self.assertEquals('false', json.dumps(json_compatible(False)))

    def test_unicode(self):
        self.assertEquals(u'foo', json_compatible(u'foo'))
        self.assertIsInstance(json_compatible(u'foo'), unicode)
        self.assertEquals('"foo"', json.dumps(json_compatible('foo')))

    def test_unicode_with_umlaut(self):
        self.assertEquals(u'Hall\xf6chen', json_compatible(u'Hall\xf6chen'))
        self.assertEquals('"Hall\\u00f6chen"',
                          json.dumps(json_compatible(u'Hall\xf6chen')))

    def test_string_is_converted_to_unicode(self):
        # Standard library JSON works with unicode.
        self.assertEquals(u'foo', json_compatible('foo'))
        self.assertIsInstance(json_compatible('foo'), unicode)
        self.assertEquals('"foo"', json.dumps(json_compatible('foo')))

    def test_string_with_umlaut(self):
        # Standard library JSON works with unicode.
        self.assertEquals(u'Hall\xf6chen', json_compatible('Hallöchen'))
        self.assertEquals('"Hall\\u00f6chen"',
                          json.dumps(json_compatible('Hallöchen')))

    def test_int(self):
        self.assertEquals(42, json_compatible(42))
        self.assertIsInstance(json_compatible(42), int)
        self.assertEquals('42', json.dumps(json_compatible(42)))

    def test_long(self):
        self.assertEquals(10L, json_compatible(10L))
        self.assertIsInstance(json_compatible(10L), long)
        self.assertEquals('10', json.dumps(json_compatible(10L)))

    def test_float(self):
        self.assertEquals(1.4, json_compatible(1.4))
        self.assertIsInstance(json_compatible(1.4), float)
        self.assertEquals('1.4', json.dumps(json_compatible(1.4)))

    def test_list(self):
        self.assertEquals(['foo'], json_compatible(['foo']))
        self.assertEquals('["foo"]', json.dumps(json_compatible(['foo'])))
        self.assertIsInstance(json_compatible(['foo'])[0],
                              unicode,
                              'List values should be converted recursively.')

    def test_persistent_list(self):
        value = PersistentList(['foo'])
        self.assertEquals(['foo'], json_compatible(value))
        self.assertEquals('["foo"]', json.dumps(json_compatible(value)))
        self.assertIsInstance(json_compatible(value)[0],
                              unicode,
                              'PersistentList values should be converted'
                              ' recursively.')

    def test_tuple(self):
        # Tuples are converted to list (json would do that anyway and
        # it is easier to implement it with map).
        self.assertEquals(['foo', None], json_compatible(('foo', None)))
        self.assertEquals('["foo"]', json.dumps(json_compatible(('foo', ))))
        self.assertIsInstance(json_compatible(('foo',))[0],
                              unicode,
                              'Tuple values should be converted recursively.')

    def test_frozenset(self):
        self.assertEquals([[1, 1], [2, 2]],
                          sorted(json_compatible(frozenset([(1, 1), (2, 2)]))))

    def test_set(self):
        self.assertEquals([[1, 1], [2, 2]],
                          sorted(json_compatible(set([(1, 1), (2, 2)]))))

    def test_dict(self):
        self.assertEquals({u'foo': True,
                           u'bar': None,
                           u'baz': 3},
                          json_compatible({'foo': True,
                                           'bar': None,
                                           'baz': 3}))
        self.assertEquals('{"foo": "bar"}',
                          json.dumps(json_compatible({'foo': 'bar'})))
        self.assertIsInstance(json_compatible({'foo': 'bar'}.keys()[0]),
                              unicode,
                              'Dict keys should be converted recursively.')
        self.assertIsInstance(json_compatible({'foo': 'bar'}.values()[0]),
                              unicode,
                              'Dict values should be converted recursively.')

    def test_dict_empty(self):
        self.assertEquals({}, json_compatible({}))
        self.assertEquals('{}', json.dumps(json_compatible({})))

    def test_persistent_mapping(self):
        value = PersistentMapping({'foo': 'bar'})
        self.assertEquals({u'foo': u'bar'}, json_compatible(value))
        self.assertEquals('{"foo": "bar"}', json.dumps(json_compatible(value)))
        self.assertIsInstance(json_compatible(value.keys()[0]),
                              unicode,
                              'Dict keys should be converted recursively.')
        self.assertIsInstance(json_compatible(value.values()[0]),
                              unicode,
                              'Dict values should be converted recursively.')

    def test_python_datetime(self):
        value = DateTime('2015/11/23 19:45:55.649027 GMT+3').asdatetime()
        self.assertEquals(u'2015-11-23T19:45:55+03:00',
                          json_compatible(value))
        self.assertEquals('"2015-11-23T19:45:55+03:00"',
                          json.dumps(json_compatible(value)))

    def test_zope_DateTime(self):
        value = DateTime('2015/11/23 19:45:55.649027 GMT+3')
        self.assertEquals(u'2015-11-23T19:45:55+03:00',
                          json_compatible(value))
        self.assertEquals('"2015-11-23T19:45:55+03:00"',
                          json.dumps(json_compatible(value)))

    def test_date(self):
        value = date(2015, 11, 23)
        self.assertEquals(u'2015-11-23', json_compatible(value))
        self.assertEquals('"2015-11-23"', json.dumps(json_compatible(value)))

    def test_time(self):
        value = time(19, 45, 55)
        self.assertEquals(u'19:45:55', json_compatible(value))
        self.assertEquals('"19:45:55"', json.dumps(json_compatible(value)))

    def test_timedelta(self):
        self.assertEquals(9.58, json_compatible(timedelta(seconds=9.58)))

    def test_broken_relation_value(self):
        self.assertEquals(None, json_compatible(RelationValue(12345)))

    def test_relation_value(self):
        portal = self.layer['portal']
        doc1 = portal[portal.invokeFactory(
            'DXTestDocument', id='doc1',
            title='Document 1',
            description='Description',
        )]
        intids = getUtility(IIntIds)
        self.assertEquals(
            {'@id': 'http://nohost/plone/doc1',
             '@type': 'DXTestDocument',
             'title': 'Document 1',
             'description': 'Description',
             'review_state': 'private'},
            json_compatible(RelationValue(intids.getId(doc1))))

    def test_i18n_message(self):
        _ = MessageFactory('plone.restapi.tests')
        msg = _(u'message_id', default=u'default message')
        self.assertEquals(u'default message', json_compatible(msg))

    def test_missing_value(self):
        self.assertEquals(None, json_compatible(Missing.Value))
