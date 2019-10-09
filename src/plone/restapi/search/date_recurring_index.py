# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.restapi.interfaces import IIndexQueryParser
from plone.restapi.search.query import BaseIndexQueryParser
from Products.DateRecurringIndex.index import DateRecurringIndex
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IIndexQueryParser)
@adapter(DateRecurringIndex, Interface, Interface)
class DateRecurringIndexQueryParser(BaseIndexQueryParser):

    query_value_type = DateTime
    query_options = {"range": str}
