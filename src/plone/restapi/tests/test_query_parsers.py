# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.restapi.exceptions import QueryParsingError
from plone.restapi.search.query import BaseIndexQueryParser
from plone.restapi.search.query import BooleanIndexQueryParser
from plone.restapi.search.query import DateIndexQueryParser
from plone.restapi.search.query import DateRangeIndexQueryParser
from plone.restapi.search.query import ExtendedPathIndexQueryParser
from plone.restapi.search.query import FieldIndexQueryParser
from plone.restapi.search.query import KeywordIndexQueryParser
from plone.restapi.search.query import UUIDIndexQueryParser
from plone.restapi.search.query import ZCTextIndexQueryParser

import unittest


class TestBaseIndexQueryParser(unittest.TestCase):
    def test_casts_simple_query_to_string(self):
        qp = BaseIndexQueryParser()
        self.assertEqual("42", qp.parse(42))

    def test_casts_complex_query_values_to_string(self):
        qp = BaseIndexQueryParser()
        self.assertEqual({"query": "42"}, qp.parse({"query": 42}))

    def test_casts_query_values_in_sequences(self):
        qp = BaseIndexQueryParser()
        self.assertEqual(["23", "42"], qp.parse([23, 42]))
        self.assertEqual(["23", "42"], qp.parse((23, 42)))

    def test_raises_on_missing_query_key_for_complex_queries(self):
        qp = BaseIndexQueryParser()
        with self.assertRaises(QueryParsingError):
            qp.parse({})


class TestZCTextIndexQueryParser(unittest.TestCase):
    def test_casts_simple_query_to_string(self):
        qp = ZCTextIndexQueryParser()
        self.assertEqual("42", qp.parse(42))

    def test_casts_complex_query_values_to_string(self):
        qp = ZCTextIndexQueryParser()
        self.assertEqual({"query": "42"}, qp.parse({"query": 42}))


class TestKeywordIndexQueryParser(unittest.TestCase):
    def test_returns_simple_query_unchanged(self):
        qp = KeywordIndexQueryParser()
        self.assertEqual("keyword", qp.parse("keyword"))
        self.assertEqual(42, qp.parse(42))

    def test_returns_complex_query_values_unchanged(self):
        qp = KeywordIndexQueryParser()
        self.assertEqual({"query": "keyword"}, qp.parse({"query": "keyword"}))
        self.assertEqual({"query": 42}, qp.parse({"query": 42}))

    def test_casts_operator_option_to_string(self):
        qp = KeywordIndexQueryParser()
        self.assertEqual(
            {"operator": "42", "query": "keyword"},
            qp.parse({"operator": 42, "query": "keyword"}),
        )

    def test_casts_range_option_to_string(self):
        qp = KeywordIndexQueryParser()
        self.assertEqual(
            {"range": "42", "query": "keyword"},
            qp.parse({"range": 42, "query": "keyword"}),
        )


class TestBooleanIndexQueryParser(unittest.TestCase):
    def test_casts_simple_query_to_boolean(self):
        qp = BooleanIndexQueryParser()
        self.assertEqual(True, qp.parse("True"))
        self.assertEqual(True, qp.parse("true"))
        self.assertEqual(True, qp.parse("1"))
        self.assertEqual(False, qp.parse("False"))
        self.assertEqual(False, qp.parse("false"))
        self.assertEqual(False, qp.parse("0"))

    def test_casts_complex_query_values_to_boolean(self):
        qp = BooleanIndexQueryParser()
        self.assertEqual({"query": True}, qp.parse({"query": "True"}))
        self.assertEqual({"query": True}, qp.parse({"query": "true"}))
        self.assertEqual({"query": True}, qp.parse({"query": "1"}))
        self.assertEqual({"query": False}, qp.parse({"query": "False"}))
        self.assertEqual({"query": False}, qp.parse({"query": "false"}))
        self.assertEqual({"query": False}, qp.parse({"query": "0"}))

    def test_raises_for_invalid_query_type(self):
        qp = BooleanIndexQueryParser()
        with self.assertRaises(QueryParsingError):
            qp.parse(42)


class TestFieldIndexQueryParser(unittest.TestCase):
    def test_returns_simple_query_unchanged(self):
        qp = FieldIndexQueryParser()
        self.assertEqual("foo", qp.parse("foo"))
        self.assertEqual(42, qp.parse(42))

    def test_returns_complex_query_values_unchanged(self):
        qp = FieldIndexQueryParser()
        self.assertEqual({"query": "foo"}, qp.parse({"query": "foo"}))
        self.assertEqual({"query": 42}, qp.parse({"query": 42}))

    def test_casts_range_option_to_string(self):
        qp = FieldIndexQueryParser()
        self.assertEqual(
            {"range": "42", "query": "/path"}, qp.parse({"range": 42, "query": "/path"})
        )


class TestExtendedPathIndexQueryParser(unittest.TestCase):
    def test_casts_simple_query_to_string(self):
        qp = ExtendedPathIndexQueryParser()
        self.assertEqual("42", qp.parse(42))

    def test_casts_complex_query_values_to_string(self):
        qp = ExtendedPathIndexQueryParser()
        self.assertEqual({"query": "42"}, qp.parse({"query": 42}))

    def test_casts_level_option_to_int(self):
        qp = ExtendedPathIndexQueryParser()
        self.assertEqual(
            {"level": 3, "query": "/path"}, qp.parse({"level": "3", "query": "/path"})
        )

    def test_casts_operator_option_to_string(self):
        qp = ExtendedPathIndexQueryParser()
        self.assertEqual(
            {"operator": "42", "query": "/path"},
            qp.parse({"operator": 42, "query": "/path"}),
        )

    def test_casts_depth_option_to_int(self):
        qp = ExtendedPathIndexQueryParser()
        self.assertEqual(
            {"depth": 3, "query": "/path"}, qp.parse({"depth": "3", "query": "/path"})
        )

    def test_casts_navtree_option_to_int(self):
        qp = ExtendedPathIndexQueryParser()
        self.assertEqual(
            {"navtree": False, "query": "/path"},
            qp.parse({"navtree": 0, "query": "/path"}),
        )
        self.assertEqual(
            {"navtree": True, "query": "/path"},
            qp.parse({"navtree": 1, "query": "/path"}),
        )

    def test_casts_navtree_start_option_to_int(self):
        qp = ExtendedPathIndexQueryParser()
        self.assertEqual(
            {"navtree_start": 42, "query": "/path"},
            qp.parse({"navtree_start": "42", "query": "/path"}),
        )


class TestDateIndexQueryParser(unittest.TestCase):
    def test_casts_simple_query_to_zope_date_time(self):
        qp = DateIndexQueryParser()
        self.assertEqual(DateTime("2016/12/24 00:00:00 GMT+0"), qp.parse("2016-12-24"))

    def test_casts_complex_query_values_to_zope_date_time(self):
        qp = DateIndexQueryParser()
        self.assertEqual(
            {"query": DateTime("2016/12/24 00:00:00 GMT+0")},
            qp.parse({"query": "2016-12-24"}),
        )

    def test_casts_range_option_to_string(self):
        qp = DateIndexQueryParser()
        self.assertEqual(
            {"range": "42", "query": DateTime("2016/12/24 00:00:00 GMT+0")},
            qp.parse({"range": 42, "query": "2016-12-24"}),
        )


class TestDateRangeIndexQueryParser(unittest.TestCase):
    def test_casts_simple_query_to_zope_date_time(self):
        qp = DateRangeIndexQueryParser()
        self.assertEqual(DateTime("2016/12/24 00:00:00 GMT+0"), qp.parse("2016-12-24"))

    def test_casts_complex_query_values_to_zope_date_time(self):
        qp = DateRangeIndexQueryParser()
        self.assertEqual(
            {"query": DateTime("2016/12/24 00:00:00 GMT+0")},
            qp.parse({"query": "2016-12-24"}),
        )


class TestUUIDIndexQueryParser(unittest.TestCase):
    def test_casts_simple_query_to_string(self):
        qp = UUIDIndexQueryParser()
        self.assertEqual("42", qp.parse(42))

    def test_casts_complex_query_values_to_string(self):
        qp = UUIDIndexQueryParser()
        self.assertEqual({"query": "42"}, qp.parse({"query": 42}))

    def test_casts_range_option_to_string(self):
        qp = UUIDIndexQueryParser()
        self.assertEqual(
            {"range": "42", "query": "<UID>"}, qp.parse({"range": 42, "query": "<UID>"})
        )
