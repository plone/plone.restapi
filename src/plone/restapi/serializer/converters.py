# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone.utils import safe_unicode
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.app.textfield.interfaces import IRichTextValue
from plone.restapi.interfaces import IJsonCompatible
from z3c.relationfield.interfaces import IRelationValue
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.interface import implementer


def json_compatible(value):
    """The json_compatible function converts any value to JSON compatible
    data when possible, raising a TypeError for unsupported values.
    This is done by using the IJsonCompatible converters.

    Be aware that adapting the value `None` will result in a component
    lookup error unless `None` is passed in as default value.
    Because of that the `json_compatible` helper method should always be
    used for converting values that may be None.
    """
    return IJsonCompatible(value, None)


@adapter(Interface)
@implementer(IJsonCompatible)
def default_converter(value):
    if value is None:
        return value

    if type(value) in (unicode, bool, int, float, long):
        return value

    raise TypeError(
        'No converter for making'
        ' {0!r} ({1}) JSON compatible.'.format(value, type(value)))


@adapter(str)
@implementer(IJsonCompatible)
def string_converter(value):
    return safe_unicode(value, getSiteEncoding(getSite()))


@adapter(list)
@implementer(IJsonCompatible)
def list_converter(value):
    return map(json_compatible, value)


@adapter(PersistentList)
@implementer(IJsonCompatible)
def persistent_list_converter(value):
    return list_converter(value)


@adapter(tuple)
@implementer(IJsonCompatible)
def tuple_converter(value):
    return map(json_compatible, value)


@adapter(frozenset)
@implementer(IJsonCompatible)
def frozenset_converter(value):
    return map(json_compatible, value)


@adapter(set)
@implementer(IJsonCompatible)
def set_converter(value):
    return map(json_compatible, value)


@adapter(dict)
@implementer(IJsonCompatible)
def dict_converter(value):
    if value == {}:
        return {}

    keys, values = zip(*value.items())
    keys = map(json_compatible, keys)
    values = map(json_compatible, values)
    return dict(zip(keys, values))


@adapter(PersistentMapping)
@implementer(IJsonCompatible)
def persistent_mapping_converter(value):
    return dict_converter(value)


@adapter(datetime)
@implementer(IJsonCompatible)
def python_datetime_converter(value):
    return json_compatible(DateTime(value))


@adapter(DateTime)
@implementer(IJsonCompatible)
def zope_DateTime_converter(value):
    return json_compatible(value.ISO8601())


@adapter(date)
@implementer(IJsonCompatible)
def date_converter(value):
    return json_compatible(value.isoformat())


@adapter(time)
@implementer(IJsonCompatible)
def time_converter(value):
    return json_compatible(value.isoformat())


@adapter(timedelta)
@implementer(IJsonCompatible)
def timedelta_converter(value):
    return json_compatible(value.total_seconds())


@adapter(IRichTextValue)
@implementer(IJsonCompatible)
def richtext_converter(value):
    return {
        u'data': json_compatible(value.raw),
        u'content-type': json_compatible(value.mimeType),
        u'encoding': json_compatible(value.encoding),
    }


@adapter(IRelationValue)
@implementer(IJsonCompatible)
def relationvalue_converter(value):
    if value.to_object:
        return json_compatible(value.to_object.absolute_url())
