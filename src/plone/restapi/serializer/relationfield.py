# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from z3c.relationfield.interfaces import IRelationValue
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer


@adapter(IRelationValue)
@implementer(IJsonCompatible)
def relationvalue_converter(value):
    if value.to_object:
        summary = getMultiAdapter(
            (value.to_object, getRequest()), ISerializeToJsonSummary)()
        return json_compatible(summary)
