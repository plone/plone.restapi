# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.textfield import RichText
from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.restapi.utils import get_object_schema
from plone.restapi.interfaces import IContext
from plone.restapi.interfaces import ISerializeToJson

from zope.site.hooks import getSite
from zope.schema import Datetime
from zope.interface import implementer
from zope.component import adapter
from zope.component import getUtility


try:
    from Products.CMFPlone.factory import _IMREALLYPLONE5  # noqa
except ImportError:
    PLONE_5 = False  # pragma: no cover
else:
    PLONE_5 = True  # pragma: no cover


@implementer(ISerializeToJson)
@adapter(IPloneSiteRoot)
def SerializeSiteRootToJson(context):
    result = {
        '@context': IContext(context),
        '@id': context.absolute_url(),
        '@type': 'SiteRoot',
        'parent': {},
    }
    result['member'] = [
        {
            '@id': member.absolute_url(),
            'title': member.title,
            'description': member.description
        }
        for member_id, member in context.objectItems()
        if IContentish.providedBy(member)
    ]
    return result


@implementer(ISerializeToJson)
@adapter(IContentish)
def SerializeToJson(context):
    result = {
        '@context': IContext(context),
        '@id': context.absolute_url(),
        '@type': context.portal_type,
        'parent': {
            '@id': aq_parent(aq_inner(context)).absolute_url(),
            'title': aq_parent(aq_inner(context)).title,
            'description': aq_parent(aq_inner(context)).description
        }
    }
    if IFolderish.providedBy(context):
        result['member'] = [
            {
                '@id': member.absolute_url(),
                '@type': member.portal_type,
                'title': member.title,
                'description': member.description
            }
            for member_id, member in context.objectItems()
        ]
    if ICollection.providedBy(context):
        portal = getSite()
        result['member'] = [
            {
                '@id': '{0}/{1}'.format(
                    portal.absolute_url(),
                    '/'.join(member.getPhysicalPath())
                ),
                '@type': member.portal_type,
                'title': member.title,
                'description': member.description
            }
            for member in context.results()
        ]
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
            # Image
            elif isinstance(value, NamedBlobImage):
                result[title] = '{0}/@@images/{1}'.format(
                    context.absolute_url(),
                    title
                )
            # File
            elif isinstance(value, NamedBlobFile):
                result[title] = '{0}/{1}'.format(
                    context.absolute_url(),
                    value.filename
                )
            else:
                result[title] = str(value)

    return result


@implementer(ISerializeToJson)
@adapter(IFile)
def SerializeFileToJson(context):
    result = {
        '@context': IContext(context),
        '@id': context.absolute_url(),
        '@type': 'File',
        'parent': {
            '@id': aq_parent(aq_inner(context)).absolute_url(),
            'title': aq_parent(aq_inner(context)).title,
            'description': aq_parent(aq_inner(context)).description
        },
        'title': context.title,
        'description': context.description,
        'download': '{0}/@@download'.format(context.absolute_url()),
    }
    return result


@implementer(ISerializeToJson)
@adapter(IImage)
def SerializeImageToJson(context):
    if PLONE_5:
        from plone.registry.interfaces import IRegistry
        registry = getUtility(IRegistry)
        from Products.CMFPlone.interfaces import IImagingSchema
        imaging_settings = registry.forInterface(
            IImagingSchema,
            prefix='plone'
        )
        allowed_sizes = imaging_settings.allowed_sizes
    else:
        ptool = getUtility(IPropertiesTool)
        image_properties = ptool.imaging_properties
        allowed_sizes = image_properties.getProperty('allowed_sizes')
    result = {
        '@context': IContext(context),
        '@id': context.absolute_url(),
        '@type': 'Image',
        'parent': {
            '@id': aq_parent(aq_inner(context)).absolute_url(),
            'title': aq_parent(aq_inner(context)).title,
            'description': aq_parent(aq_inner(context)).description
        },
        'title': context.title,
        'description': context.description,
        'download': '{0}/@@download'.format(context.absolute_url()),
        'scales': {
            x.split(' ')[0]: '{0}/@@images/image/{1}'.format(
                context.absolute_url(),
                x.split(' ')[0]
            ) for x in allowed_sizes
        }
    }
    return result
