# -*- coding: utf-8 -*-

from Acquisition import aq_base
from plone import api
from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.app.portlets.portlets.navigation import Renderer
from plone.app.textfield.interfaces import IRichText
from plone.memoize import forever
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever
from plone.portlets.utils import hashPortletInfo
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from Products.CMFPlone import utils
from ZODB.POSException import ConflictError
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import providedBy
from zope.publisher.interfaces import IRequest
from zope.schema import getFields
from zope.schema.interfaces import IField

import logging


# import six


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

            # To be able to customize serializers per portlet type, we try to
            # lookup for a named adapter first. The name is the portlet type

            # TODO: the serializer should ideally have the same discriminators
            # as the portlet renderer: context, request, view=service, manager,
            # data.
            type_, schema = get_portlet_info(assignment)
            serializer = queryMultiAdapter(
                (assignment, self.context, self.request),
                ISerializeToJson,
                name=type_
            )

            if not serializer:
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


@forever.memoize
def getPortletSchemata():  # noqa
    return dict([(iface, name)
                 for name, iface
                 in getUtilitiesFor(IPortletTypeInterface)])


def get_portlet_info(assignment):
    """ Returns the portlet type (like portlet.Navigation) and schema
    """

    # Adapted from
    # plone.app.portlets.exportimport.portlets._extractPortlets
    portlet_schemata = getPortletSchemata()
    type_ = None
    schema = None

    for schema in providedBy(assignment).flattened():
        type_ = portlet_schemata.get(schema, None)

        if type_ is not None:
            break

    return type_, schema


@implementer(ISerializeToJson)
@adapter(IPortletAssignment, Interface, IRequest)
class PortletSerializer(object):

    def __init__(self, assignment, context, request):
        self.assignment = assignment
        self.context = context
        self.request = request

    def __call__(self):

        if not getattr(self.assignment, '__portlet_metadata__', False):
            return None

        portlet_metadata = self.assignment.__portlet_metadata__

        content_url = self.context.absolute_url()
        url = '{0}/@portlets/{1}/{2}'.format(
            content_url,
            portlet_metadata['manager'],
            portlet_metadata['name'])

        phash = portlet_metadata['hash']

        if isinstance(phash, bytes):
            phash = phash.decode("utf8")

        result = {
            '@id': url,
            'portlet_id': portlet_metadata['name'],
            'portlet_manager': portlet_metadata['manager'],
            'portlet_category': portlet_metadata['category'],
            'portlet_key': portlet_metadata['key'],
            'portlet_hash': phash,
        }

        type_, schema = get_portlet_info(self.assignment)

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


class NavigationPortletSerializer(PortletSerializer):
    """ Portlet serializer for navigation portlet
    """

    def __call__(self):
        res = super(NavigationPortletSerializer, self).__call__()
        renderer = NavtreePortletRenderer(
            self.context,
            self.request,
            None,
            None,
            self.assignment
        )

        res['navigationportlet'] = renderer.render()

        return res


def get_url(item):
    if not item:
        return None

    if hasattr(aq_base(item), 'getURL'):
        # Looks like a brain

        return item.getURL()

    return item.absolute_url()


def get_id(item):
    if not item:
        return None
    getId = getattr(item, 'getId')

    if not utils.safe_callable(getId):
        # Looks like a brain

        return getId

    return getId()


def get_view_url(context):
    registry = getUtility(IRegistry)
    view_action_types = registry.get(
        'plone.types_use_view_action_in_listings', [])
    item_url = get_url(context)
    name = get_id(context)

    if getattr(context, 'portal_type', {}) in view_action_types:
        item_url += '/view'
        name += '/view'

    return name, item_url


class NavtreePortletRenderer(Renderer):
    def render(self):
        res = {
            'title': self.title(),
            'url': self.heading_link_target(),
            'has_custom_name': bool(self.hasName()),
            'items': [],
        }

        if self.include_top():
            root = self.navigation_root()

            if utils.safe_hasattr(self.context, 'getRemoteUrl'):
                root_url = root.getRemoteUrl()
            else:
                cid, root_url = get_view_url(root)

            root_is_portal = self.root_is_portal()
            root_title = ('Home'
                          if root_is_portal else root.pretty_title_or_id())
            root_type = ('plone-site'
                         if root_is_portal else utils.normalizeString(
                             root.portal_type, context=root))
            normalized_id = utils.normalizeString(root.Title(), context=root)

            if root_is_portal:
                state = ''
            else:
                state = api.content.get_state(root)

            res['items'].append({
                '@id': root.absolute_url(),
                'description': root.Description() or '',
                'href': root_url,
                'icon': '',
                'is_current': bool(self.root_item_class()),
                'is_folderish': True,
                'is_in_path': True,
                'items': [],
                'normalized_id': normalized_id,
                'thumb': '',
                'title': root_title,
                'type': root_type,
                'review_state': state,
            })

        res['items'] = self.createNavTree()

        return res

    def recurse(self, children, level, bottomLevel):
        # TODO: we should avoid recursion. This is just a rewrite of the TAL
        # template, but ideally we should use a dequeue structure to avoid
        # recursion problems.

        res = []

        show_thumbs = not self.data.no_thumbs
        show_icons = not self.data.no_icons

        thumb_scale = self.thumb_scale
        image_scale = getMultiAdapter((api.portal.get(), self.request),
                                      name='image_scale')

        for node in children:
            brain = node['item']

            icon = ''

            if show_icons:
                if (node['portal_type'] == 'File'):
                    icon = self.getMimeTypeIcon(node)

            has_thumb = brain.getIcon
            thumb = ''

            if show_thumbs and has_thumb and thumb_scale:
                thumb = image_scale.tag(brain, 'image', scale=thumb_scale)

            show_children = node['show_children']
            item_remote_url = node['getRemoteUrl']
            use_remote_url = node['useRemoteUrl']
            item_url = node['getURL']
            item = {
                '@id': item_url,
                'description': node['Description'],
                'href': item_remote_url if use_remote_url else item_url,
                'icon': icon,
                'is_current': node['currentItem'],
                'is_folderish': node['show_children'],
                'is_in_path': node['currentParent'],
                'items': [],
                'normalized_id': node['normalized_id'],
                'review_state': node['review_state'] or '',
                'thumb': thumb,
                'title': node['Title'],
                'type': utils.normalizeString(node['portal_type']),
            }

            if children and show_children and \
                    ((bottomLevel < level) or (bottomLevel == 0)):
                children = node['children']
                item['items'] = self.recurse(
                    children, level=level + 1, bottomLevel=bottomLevel)

            res.append(item)

        return res


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
