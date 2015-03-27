# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.textfield import RichText
from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.restapi.utils import get_object_schema
from plone.restapi.interfaces import ISerializeToJson

from zope.site.hooks import getSite
from zope.schema import Datetime
from zope.interface import implementer
from zope.component import adapter
from zope.component import getUtility

import json


@implementer(ISerializeToJson)
@adapter(IPloneSiteRoot)
def SerializeSiteRootToJson(context):
    result = {
        "@context": "http://www.w3.org/ns/hydra/context.jsonld",
        "@id": context.absolute_url(),
        '@type': 'Collection',
        'portal_type': 'SiteRoot'
    }
    result['member'] = [
        {
            '@id': member.absolute_url() + '/@@json',
            'title': member.title,
            'description': member.description
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
                'title': member.title,
                'description': member.description
            }
            for member_id, member in context.objectItems()
        ]
    elif ICollection.providedBy(context):
        result['@type'] = 'Collection'
        portal = getSite()
        result['member'] = [
            {
                '@id': '{0}/{1}/@@json'.format(
                    portal.absolute_url(),
                    '/'.join(member.getPhysicalPath())
                ),
                'title': member.title,
                'description': member.description
            }
            for member in context.results()
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


@implementer(ISerializeToJson)
@adapter(IFile)
def SerializeFileToJson(context):
    result = {
        "@context": "http://www.w3.org/ns/hydra/context.jsonld",
        "@id": context.absolute_url(),
        '@type': 'Resource',
        'portal_type': 'File',
        'title': context.title,
        'description': context.description,
        'download': '{0}/@@download'.format(context.absolute_url()),
    }
    return json.dumps(result, indent=2, sort_keys=True)


@implementer(ISerializeToJson)
@adapter(IImage)
def SerializeImageToJson(context):
    ptool = getUtility(IPropertiesTool)
    image_properties = ptool.imaging_properties
    allowed_sizes = image_properties.getProperty('allowed_sizes')
    result = {
        "@context": "http://www.w3.org/ns/hydra/context.jsonld",
        "@id": context.absolute_url(),
        '@type': 'Resource',
        'portal_type': 'Image',
        'title': context.title,
        'description': context.description,
        'download': '{0}/@@download'.format(context.absolute_url()),
        'versions': [
            '{0}/@@images/image/{1}'.format(
                context.absolute_url(),
                x.split(' ')[0]
            ) for x in allowed_sizes
        ]
    }
    return json.dumps(result, indent=2, sort_keys=True)
