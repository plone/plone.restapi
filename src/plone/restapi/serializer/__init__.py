# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import IFolderish
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.restapi import HAS_PLONE_APP_CONTENTTYPES
from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from plone.dexterity.utils import iterSchemata
from plone.supermodel.utils import mergedTaggedValueDict

from zope.site.hooks import getSite
from zope.interface import implementer
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.schema import getFields
from zope.security.interfaces import IPermission


def lookup_field_serializer(context, field):
    objects = (field, context, context.REQUEST)

    # first, try to lookup a serializer named with the full
    # dottedname of the field, e.g.:
    # "my.package.behaviors.IPreview.preview_image"
    name = '.'.join((field.interface.__identifier__, field.__name__))
    serializer = queryMultiAdapter(objects, IFieldSerializer, name=name)
    if serializer is not None:
        return serializer

    # then, lookup the default serializer for this type of field.
    return getMultiAdapter(objects, IFieldSerializer)


@implementer(ISerializeToJson)
@adapter(IPloneSiteRoot)
def SerializeSiteRootToJson(context):
    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
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
        for member in context.objectValues()
        if IContentish.providedBy(member)
    ]
    return result


@implementer(ISerializeToJson)
@adapter(IContentish)
def SerializeToJson(context):
    result = {
        '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
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
                'title': member.title,
                'description': member.description
            }
            for member in context.objectValues()
        ]

    if HAS_PLONE_APP_CONTENTTYPES:
        # Conditional import in order to avoid a hard dependency on p.a.ct
        from plone.app.contenttypes.interfaces import ICollection

        if ICollection.providedBy(context):
            portal = getSite()
            result['member'] = [
                {
                    '@id': '{0}/{1}'.format(
                        portal.absolute_url(),
                        '/'.join(member.getPhysicalPath())
                    ),
                    'title': member.title,
                    'description': member.description
                }
                for member in context.results()
            ]

    for schema in iterSchemata(context):
        for field_name, field in getFields(schema).items():
            read_permissions = mergedTaggedValueDict(
                schema, READ_PERMISSIONS_KEY)

            if not check_permission(context, read_permissions.get(field_name)):
                continue
            value = lookup_field_serializer(context, field)()
            result[json_compatible(field_name)] = value

    return result


def check_permission(context, permission_name):
    permission_cache = {}

    sm = getSecurityManager()
    if permission_name is None:
        return True

    if permission_name not in permission_cache:
        permission = queryUtility(IPermission,
                                  name=permission_name)
        if permission is None:
            permission_cache[permission_name] = True
        else:
            permission_cache[permission_name] = bool(
                sm.checkPermission(permission.title, context))
    return permission_cache[permission_name]
