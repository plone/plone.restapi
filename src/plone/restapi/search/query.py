# -*- coding: utf-8 -*-
"""
The adapters in this module are responsible for turning back a catalog query
that has been serialized (to a HTTP query string or JSON) into a query that is
suitable for passing to catalog.searchResults().

The main issue here is typing of query values and query options. See docs for
the IZCatalogCompatibleQuery and IIndexQueryParser interfaces for details.

The adapters provided in this module cover the index types present in default
Plone 4.3 / 5.0 installations.

Index types used in a default Plone 4.3:

- BooleanIndex
- DateIndex
- DateRangeIndex
- ExtendedPathIndex
- FieldIndex
- GopipIndex (not queriable)
- KeywordIndex
- UUIDIndex
- ZCTextIndex

Plone 5.0:

- DateRecurringIndex (plus all of the above)

The adapter for DateRecurringIndex is in a separate module and registered
conditionally in order to avoid breaking compatibility with vanilla Plone 4.3.
"""

from DateTime import DateTime
from DateTime.interfaces import SyntaxError as DTSyntaxError
from plone.restapi.exceptions import QueryParsingError
from plone.restapi.interfaces import IIndexQueryParser
from plone.restapi.interfaces import IZCatalogCompatibleQuery
from Products.CMFCore.utils import getToolByName
from Products.ExtendedPathIndex.ExtendedPathIndex import ExtendedPathIndex
from Products.PluginIndexes.BooleanIndex.BooleanIndex import BooleanIndex
from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
from Products.PluginIndexes.DateRangeIndex.DateRangeIndex import DateRangeIndex
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex
from Products.PluginIndexes.UUIDIndex.UUIDIndex import UUIDIndex
from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

import logging


log = logging.getLogger(__name__)

# Marker value to signal that query values may be of an arbitrary type
ANY_TYPE = object()


@implementer(IZCatalogCompatibleQuery)
@adapter(Interface, Interface)
class ZCatalogCompatibleQueryAdapter(object):
    """Converts a Python dictionary representing a catalog query, but with
    possibly wrong value types, to a ZCatalog compatible query dict suitable
    for passing to catalog.searchResults().

    See the IZCatalogCompatibleQuery interface documentation for details.
    """

    global_query_params = {
        'sort_on': str,
        'sort_order': str,
        'sort_limit': int,
        'b_start': int,
        'b_size': int,
    }

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.catalog = getToolByName(self.context, 'portal_catalog')

    def get_index(self, name):
        return self.catalog._catalog.indexes.get(name)

    def parse_query_param(self, idx_name, idx_query):
        _type = self.global_query_params[idx_name]
        return _type(idx_query)

    def __call__(self, query):
        for idx_name, idx_query in query.items():
            if idx_name in self.global_query_params:
                # It's a query-wide parameter like 'sort_on'
                query[idx_name] = self.parse_query_param(idx_name, idx_query)
                continue

            # Then check for each index present in the query if there is an
            # IIndexQueryParser that knows how to deserialize any values
            # that could not be serialized in a query string or JSON
            index = self.get_index(idx_name)
            if index is None:
                log.warn("No such index: %r" % idx_name)
                continue

            query_opts_parser = getMultiAdapter(
                (index, self.context, self.request), IIndexQueryParser)

            if query_opts_parser is not None:
                idx_query = query_opts_parser.parse(idx_query)

            query[idx_name] = idx_query
        return query


class BaseIndexQueryParser(object):
    """Base class for IIndexQueryParser adapters.

    See the IIndexQueryParser interface documentation for details.
    """

    query_value_type = str
    query_options = {}

    def __init__(self, index=None, context=None, request=None):
        self.index = index
        self.context = context
        self.request = request

    def parse(self, idx_query):
        if isinstance(idx_query, dict):
            return self.parse_complex_query(idx_query)
        return self.parse_simple_query(idx_query)

    def parse_query_value(self, query_value):
        if self.query_value_type is ANY_TYPE:
            return query_value
        try:
            query_value = self.query_value_type(query_value)

        except (ValueError, DTSyntaxError):
            raise QueryParsingError(
                "Query value %r for index %s must be of type %r" % (
                    query_value, self.index, self.query_value_type))
        return self.query_value_type(query_value)

    def parse_simple_query(self, idx_query):
        if isinstance(idx_query, (list, tuple)):
            return [self.parse_query_value(q) for q in idx_query]
        return self.parse_query_value(idx_query)

    def parse_complex_query(self, idx_query):
        idx_query = idx_query.copy()
        parsed_query = {}

        try:
            qv = idx_query.pop('query')
            parsed_query['query'] = self.parse_simple_query(qv)
        except KeyError:
            raise QueryParsingError(
                "Query for index %r is missing a 'query' key!" % self.index)

        for opt_key, opt_value in idx_query.items():
            if opt_key in self.query_options:
                opt_type = self.query_options[opt_key]
                try:
                    parsed_query[opt_key] = opt_type(opt_value)
                except ValueError:
                    raise QueryParsingError(
                        "Value %r for query option %r (index %r) could not be"
                        " casted to %r" % (
                            opt_value, opt_key, self.index, opt_type))
            else:
                log.warn("Unrecognized query option %r for index %r" % (
                    opt_key, self.index))
                # Pass along unknown option without modification
                parsed_query[opt_key] = opt_value

        return parsed_query


@implementer(IIndexQueryParser)
@adapter(ZCTextIndex, Interface, Interface)
class ZCTextIndexQueryParser(BaseIndexQueryParser):

    query_value_type = str
    query_options = {}


@implementer(IIndexQueryParser)
@adapter(KeywordIndex, Interface, Interface)
class KeywordIndexQueryParser(BaseIndexQueryParser):

    query_value_type = ANY_TYPE
    query_options = {
        'operator': str,
        'range': str,
    }


@implementer(IIndexQueryParser)
@adapter(BooleanIndex, Interface, Interface)
class BooleanIndexQueryParser(BaseIndexQueryParser):

    query_value_type = bool
    query_options = {}

    def parse_query_value(self, query_value):
        if not str(query_value).lower() in ('true', 'false', '1', '0'):
            raise QueryParsingError(
                'Could not parse query value %r as boolean' % query_value)
        return str(query_value).lower() in ('true', '1')


@implementer(IIndexQueryParser)
@adapter(FieldIndex, Interface, Interface)
class FieldIndexQueryParser(BaseIndexQueryParser):

    query_value_type = ANY_TYPE
    query_options = {
        'range': str,
    }


@implementer(IIndexQueryParser)
@adapter(ExtendedPathIndex, Interface, Interface)
class ExtendedPathIndexQueryParser(BaseIndexQueryParser):

    query_value_type = str
    query_options = {
        'level': int,
        'operator': str,
        'depth': int,
        'navtree': bool,
        'navtree_start': int,
    }


@implementer(IIndexQueryParser)
@adapter(DateIndex, Interface, Interface)
class DateIndexQueryParser(BaseIndexQueryParser):

    query_value_type = DateTime
    query_options = {
        'range': str,
    }


@implementer(IIndexQueryParser)
@adapter(DateRangeIndex, Interface, Interface)
class DateRangeIndexQueryParser(BaseIndexQueryParser):

    query_value_type = DateTime
    query_options = {}


@implementer(IIndexQueryParser)
@adapter(UUIDIndex, Interface, Interface)
class UUIDIndexQueryParser(BaseIndexQueryParser):

    query_value_type = str
    query_options = {
        'range': str,
    }
