# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.textfield import RichText
from plone.restapi.utils import get_object_schema
from plone.restapi.interfaces import ISerializeToJson

from zope.schema import Datetime
from zope.interface import implementer
from zope.component import adapter

import json


@implementer(ISerializeToJson)
@adapter(IPloneSiteRoot)
def SerializeSiteRootToJson(context):
    result = {
        "@context": "http://www.w3.org/ns/hydra/context.jsonld",
        "@id": context.absolute_url(),
        '@type': 'Collection',
    }
    result['member'] = [
        {
            '@id': member.absolute_url() + '/@@json',
            'title': member.title
        }
        for member_id, member in context.objectItems()
        if IContentish.providedBy(member)
    ]
    return json.dumps(result, indent=2, sort_keys=True)


@implementer(ISerializeToJson)
@adapter(IContentish)
def SerializeToJson(context):
    result = {
        "@context": "http://www.w3.org/ns/hydra/context.jsonld",
        "@id": context.absolute_url(),
    }
    if IFolderish.providedBy(context):
        result['@type'] = 'Collection'
        result['member'] = [
            {
                '@id': member.absolute_url() + '/@@json',
                'title': member.title
            }
            for member_id, member in context.objectItems()
        ]
    else:
        result['@type'] = 'Resource'
    for title, schema_object in get_object_schema(context):
        value = getattr(context, title, None)
        if value is not None:
            # RichText
            if isinstance(schema_object, RichText):
                result[title] = value.output
            # DateTime
            elif isinstance(schema_object, Datetime):
                # Return DateTime in ISO-8601 format. See
                # https://pypi.python.org/pypi/DateTime/3.0 and
                # http://www.w3.org/TR/NOTE-datetime for details.
                # XXX: We might want to change that in the future.
                result[title] = value().ISO8601()
            # Tuple
            elif isinstance(value, tuple):
                result[title] = list(value)
            # List
            elif isinstance(value, list):
                result[title] = value
            # String
            elif isinstance(value, str):
                result[title] = value
            # Unicode
            elif isinstance(value, unicode):
                result[title] = value
            else:
                result[title] = str(value)
    return json.dumps(result, indent=2, sort_keys=True)
