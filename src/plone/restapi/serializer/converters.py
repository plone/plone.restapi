from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from DateTime import DateTime
from decimal import Decimal
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.app.textfield.interfaces import IRichTextValue
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IContextawareJsonCompatible
from plone.restapi.interfaces import IJsonCompatible
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.i18nmessageid.message import Message
from zope.interface import implementer
from zope.interface import Interface

import Missing
import pytz


# import re


def datetimelike_to_iso(value):
    if isinstance(value, DateTime):
        value = value.asdatetime()

    if getattr(value, "tzinfo", None):
        # timezone aware date/time objects are converted to UTC first.
        utc = pytz.timezone("UTC")
        value = value.astimezone(utc)
    if getattr(value, "microsecond", False):
        # Microseconds are normally not used in Plone
        value = value.replace(microsecond=0)
    iso = value.isoformat()
    # if value.tzinfo:
    #     # Use "Z" instead of a timezone offset of "+00:00" to indicate UTC.
    #     regex = None
    #     if isinstance(value, datetime):
    #         regex = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
    #     if isinstance(value, time):
    #         regex = re.compile(r'\d{2}:\d{2}:\d{2}')
    #     match = regex.match(iso)
    #     iso = match.group(0) + 'Z'
    return iso


def json_compatible(value, context=None):
    """The json_compatible function converts any value to JSON compatible
    data when possible, raising a TypeError for unsupported values.
    This is done by using the IJsonCompatible converters.

    Be aware that adapting the value `None` will result in a component
    lookup error unless `None` is passed in as default value.
    Because of that the `json_compatible` helper method should always be
    used for converting values that may be None.
    """
    if context is not None:
        adapter = queryMultiAdapter((value, context), IContextawareJsonCompatible)
        if adapter:
            return adapter()
    else:
        return IJsonCompatible(value, None)


@adapter(Interface)
@implementer(IJsonCompatible)
def default_converter(value):
    if value is None:
        return value

    if type(value) in (str, bool, int, float, int):
        return value

    raise TypeError(
        "No converter for making"
        " {!r} ({}) JSON compatible.".format(value, type(value))
    )


@adapter(Decimal)
@implementer(IJsonCompatible)
def decimal_converter(value):
    return safe_unicode(str(value))


@adapter(bytes)
@implementer(IJsonCompatible)
def bytes_converter(value):
    return safe_unicode(value, "utf-8")


@adapter(list)
@implementer(IJsonCompatible)
def list_converter(value):
    return list(map(json_compatible, value))


@adapter(PersistentList)
@implementer(IJsonCompatible)
def persistent_list_converter(value):
    return list_converter(value)


@adapter(tuple)
@implementer(IJsonCompatible)
def tuple_converter(value):
    return list(map(json_compatible, value))


@adapter(frozenset)
@implementer(IJsonCompatible)
def frozenset_converter(value):
    return list(map(json_compatible, value))


@adapter(set)
@implementer(IJsonCompatible)
def set_converter(value):
    return list(map(json_compatible, value))


@adapter(dict)
@implementer(IJsonCompatible)
def dict_converter(value):
    if value == {}:
        return {}

    keys, values = list(zip(*list(value.items())))
    keys = list(map(json_compatible, keys))
    values = list(map(json_compatible, values))
    return dict(list(zip(keys, values)))


@adapter(PersistentMapping)
@implementer(IJsonCompatible)
def persistent_mapping_converter(value):
    return dict_converter(value)


@adapter(datetime)
@implementer(IJsonCompatible)
def python_datetime_converter(value):
    return json_compatible(datetimelike_to_iso(value))


@adapter(DateTime)
@implementer(IJsonCompatible)
def zope_DateTime_converter(value):
    return json_compatible(datetimelike_to_iso(value))


@adapter(date)
@implementer(IJsonCompatible)
def date_converter(value):
    return json_compatible(datetimelike_to_iso(value))


@adapter(time)
@implementer(IJsonCompatible)
def time_converter(value):
    return json_compatible(datetimelike_to_iso(value))


@adapter(timedelta)
@implementer(IJsonCompatible)
def timedelta_converter(value):
    return json_compatible(value.total_seconds())


@adapter(IRichTextValue, IDexterityContent)
@implementer(IContextawareJsonCompatible)
class RichtextDXContextConverter:
    def __init__(self, value, context):
        self.value = value
        self.context = context

    def __call__(self):
        value = self.value
        output = value.output_relative_to(self.context)
        return {
            "data": json_compatible(output),
            "content-type": json_compatible(value.mimeType),
            "encoding": json_compatible(value.encoding),
        }


@adapter(Message)
@implementer(IJsonCompatible)
def i18n_message_converter(value):
    value = translate(value, context=getRequest())
    return value


@adapter(Missing.Value.__class__)
@implementer(IJsonCompatible)
def missing_value_converter(value):
    pass
