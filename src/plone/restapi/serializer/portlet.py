# -*- coding: utf-8 -*-
from plone import api
from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.app.textfield.interfaces import IRichText
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever
from plone.portlets.utils import hashPortletInfo
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from ZODB.POSException import ConflictError
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import providedBy
from zope.publisher.interfaces import IRequest
from zope.schema import getFields
from zope.schema.interfaces import IField

import logging


logger = logging.getLogger(__name__)

SERVICE_ID = '@portlets'


@implementer(ISerializeToJsonSummary)
@adapter(IPortletManager, Interface, IRequest)
class PortletManagerSummarySerializer(object):

    def __init__(self, manager, context, request):
        self.manager = manager
        self.context = context
        self.request = request

    def __call__(self):
        manager_id = self.manager.__name__

        content_url = self.context.absolute_url()
        url = '{0}/{1}/{2}'.format(content_url, SERVICE_ID, manager_id)

        return {
            '@id': url,
            'manager': manager_id,
        }


@implementer(ISerializeToJson)
@adapter(IPortletManager, Interface, IRequest)
class PortletManagerSerializer(object):

    def __init__(self, manager, context, request):
        self.manager = manager
        self.context = context
        self.request = request

    def filter(self, portlets):
        # Check available of the assignment.
        # TODO: We currently
        # do not use the renderer, but
        # this frequently have an available property too,
        # hiding lists if they have no items.
        # What can we do about that? Get hold of the renderer?
        filtered = []
        for p in portlets:
            try:
                if p['assignment'].available:
                    filtered.append(p)
            except ConflictError:
                raise
            except Exception as e:
                logger.exception(
                    'Error while determining assignment availability of '
                    'portlet (%r %r %r): %s' % (
                        p['category'], p['key'], p['name'], str(e)))
        return filtered

    def __call__(self):
        result = {}

        manager_id = self.manager.__name__

        content_url = self.context.absolute_url()
        url = '{0}/{1}/{2}'.format(content_url, SERVICE_ID, manager_id)

        result = {
            '@id': url,
            'manager': manager_id,
            'portlets': [],
        }

        retriever = getMultiAdapter((self.context, self.manager),
                                    IPortletRetriever)
        # The retriever only returns portlets that are visible.
        # Still need to check available.

        # Based on
        # plone.portlets.manager.PortletManagerRenderer._lazyLoadPortlets
        for portlet in self.filter(retriever.getPortlets()):
            assignment = portlet['assignment']

            info = portlet.copy()
            info['manager'] = manager_id
            hashPortletInfo(info)

            assignment.__portlet_metadata__ = {
                'key': portlet['key'],
                'category': portlet['category'],
                'name': portlet['name'],
                'manager': manager_id,
                'hash': info['hash'],
            }

            serializer = queryMultiAdapter(
                (assignment, self.context, self.request),
                ISerializeToJson
            )
            if not serializer:
                logger.warn(
                    'No serializer for portlet (%r %r %r)' % (
                        portlet['category'], portlet['key'], portlet['name']))
                continue

            portlet_json = serializer()
            if portlet_json:
                result['portlets'].append(portlet_json)

        return result


@implementer(ISerializeToJson)
@adapter(IPortletAssignment, Interface, IRequest)
class PortletSerializer(object):

    def __init__(self, assignment, context, request):
        self.assignment = assignment
        self.context = context
        self.request = request

    # todo: cache
    def getPortletSchemata(self):  # noqa
        return dict([(iface, name)
                    for name, iface
                    in getUtilitiesFor(IPortletTypeInterface)])

    def __call__(self):

        if not getattr(self.assignment, '__portlet_metadata__', False):
            return None

        portlet_metadata = self.assignment.__portlet_metadata__

        content_url = self.context.absolute_url()
        url = '{0}/@portlets/{1}/{2}'.format(
            content_url,
            portlet_metadata['manager'],
            portlet_metadata['name'])
        result = {
            '@id': url,
            'portlet_id': portlet_metadata['name'],
            'portlet_manager': portlet_metadata['manager'],
            'portlet_category': portlet_metadata['category'],
            'portlet_key': portlet_metadata['key'],
            'portlet_hash': portlet_metadata['hash'],
        }

        # Adapted from
        # plone.app.portlets.exportimport.portlets._extractPortlets
        portlet_schemata = self.getPortletSchemata()
        type_ = None
        schema = None
        for schema in providedBy(self.assignment).flattened():
            type_ = portlet_schemata.get(schema, None)
            if type_ is not None:
                break

        if type_ is not None:

            type_filter = None
            if 'type' in self.request.form.keys():
                type_filter = self.request.form.get('type')
                if not isinstance(type_filter, (list, tuple)):
                    type_filter = [type_filter]

            if type_filter and type_ not in type_filter:
                return None

            result['@type'] = type_
            data = self.assignment.data

            transformer_context = api.portal.get()
            if (portlet_metadata['category'] == 'context'):
                assignment_context_path = portlet_metadata['key']
                assignment_context = self.context.unrestrictedTraverse(
                    assignment_context_path)
                transformer_context = assignment_context

            for name, field in getFields(schema).items():
                try:
                    # todo: portlet schema permissions?
                    serializer = queryMultiAdapter(
                        (field, data, transformer_context, self.request),
                        IFieldSerializer)
                    value = serializer()
                    result[json_compatible(name)] = value
                except ConflictError:
                    raise
                except Exception as e:
                    logger.exception(
                        'Error while serializing '
                        'portlet (%r %r %r), field %s: %s' % (
                            portlet_metadata['category'],
                            portlet_metadata['key'],
                            portlet_metadata['name'],
                            str(name),
                            str(e)))

        return result


# See serializer/dxfields.py: The portlet fields
# needs both the portletdataprovider
# as well as the context. So we extend the
# default dexterity field serializers.


@adapter(IField, IPortletDataProvider, Interface, Interface)
@implementer(IFieldSerializer)
class DefaultPortletFieldSerializer(DefaultFieldSerializer):

    def __init__(self, field, portletdata, context, request):
        self.field = field
        self.portletdata = portletdata
        self.context = context
        self.request = request

    def get_value(self, default=None):
        return getattr(self.field.interface(self.portletdata),
                       self.field.__name__,
                       default)


@adapter(IRichText, IPortletDataProvider, Interface, Interface)
class RichttextPortletFieldSerializer(DefaultPortletFieldSerializer):
    def __call__(self):
        value = self.get_value()
        # self.context is the transform context of the portlet:
        return json_compatible(value, self.context)


# TODO: extension of file and image serializers from dxfields.py
