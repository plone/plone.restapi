# -*- coding: utf-8 -*-

# from Acquisition import aq_parent
# from OFS.interfaces import IApplication
# from plone.restapi.interfaces import IExpandableElement
# from plone.restapi.services import Service
# from Products.CMFPlone.browser.interfaces import INavigationTabs
# from Products.Five import BrowserView

from Acquisition import aq_base
from Acquisition import aq_inner
from plone import api
from plone.api import content
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.app.portlets.navigation import Renderer
from plone.app.textfield.interfaces import IRichText
from plone.app.uuid.utils import uuidToObject
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
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder
from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from Products.CMFPlone.interfaces import INavigationSchema
from ZODB.POSException import ConflictError
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
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

            # To be able to customize serializers per portlet type, we try to
            # lookup for a named adapter first. The name is the portlet type
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
        result = {
            '@id': url,
            'portlet_id': portlet_metadata['name'],
            'portlet_manager': portlet_metadata['manager'],
            'portlet_category': portlet_metadata['category'],
            'portlet_key': portlet_metadata['key'],
            'portlet_hash': portlet_metadata['hash'],
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

        root = self.context

        # if self.assignment.root_uid:
        #     root = uuidToObject(self.assignment.root_uid)

        # nav = PortletNavigation(root, self.request)
        # res['navtree'] = nav(
        #     depth=self.assignment.bottomLevel,
        #     includeTop=self.assignment.includeTop,
        #     currentFolderOnly=self.assignment.currentFolderOnly,
        # )

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


class NavigationTreeQueryBuilder(NavtreeQueryBuilder):
    """Build a folder tree query

    Used to build a tab subtree queries for the PortletNavigation class
    """

    def __init__(self, context, depth):
        NavtreeQueryBuilder.__init__(self, context)
        self.query["path"] = {
            "query": "/".join(context.getPhysicalPath()),
            "navtree_start": 1,
            "depth": depth - 1,
        }


def getLocalNavigationRoot(context):
    return "/".join(context.getPhysicalPath())


# nothing is customized here, just this getNavigationRoot method
class CustomNavtreeStrategy(SitemapNavtreeStrategy):

    def __init__(self, context, bottomLevel=0):
        SitemapNavtreeStrategy.__init__(self, context, None)
        self.context = context
        self.bottomLevel = bottomLevel
        self.rootPath = self.getRootPath()

    def subtreeFilter(self, node):
        sitemapDecision = SitemapNavtreeStrategy.subtreeFilter(self, node)

        if sitemapDecision is False:
            return False
        depth = node.get("depth", 0)

        if depth > 0 and self.bottomLevel > 0 and depth >= self.bottomLevel:
            return False
        else:
            return True

    def getRootPath(self, topLevel=1):
        rootPath = getLocalNavigationRoot(self.context)

        rootPath = contextPath = "/".join(self.context.getPhysicalPath())

        if not contextPath.startswith(rootPath):
            return None
        contextSubPathElements = contextPath[len(rootPath) + 1:]

        if contextSubPathElements:
            contextSubPathElements = contextSubPathElements.split("/")

            if len(contextSubPathElements) < topLevel:
                return None
            rootPath = (
                rootPath + "/" + "/".join(contextSubPathElements[:topLevel])
            )  # noqa
        else:
            return None

        return rootPath


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


class CatalogNavigationTabs(object):
    """ Gets the top level children as "tabs"
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _getNavQuery(self, currentFolderOnly):
                # check whether we only want actions
        registry = getUtility(IRegistry)
        navigation_settings = registry.forInterface(
            INavigationSchema,
            prefix="plone",
            check=False
        )
        customQuery = getattr(self.context, 'getCustomNavQuery', False)

        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        if currentFolderOnly:
            path = getLocalNavigationRoot(self.context)
        else:
            path = getNavigationRoot(self.context)

        query['path'] = {
            'query': path,
            'depth': 1
        }
        query['portal_type'] = [t for t in navigation_settings.displayed_types]
        query['sort_on'] = navigation_settings.sort_tabs_on

        if navigation_settings.sort_tabs_reversed:
            query['sort_order'] = 'reverse'
        else:
            query['sort_order'] = 'ascending'

        if navigation_settings.filter_on_workflow:
            query['review_state'] = navigation_settings.workflow_states_to_show

        query['is_default_page'] = False

        if not navigation_settings.nonfolderish_tabs:
            query['is_folderish'] = True

        return query

    def topLevelTabs(self, currentFolderOnly):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember().id
        catalog = getToolByName(context, 'portal_catalog')

        # Build result dict
        result = []

        query = self._getNavQuery(currentFolderOnly)

        rawresult = catalog.searchResults(query)

        def _get_url(item):
            if item.getRemoteUrl and not member == item.Creator:
                return (get_id(item), item.getRemoteUrl)

            return get_view_url(item)

        # now add the content to results

        for item in rawresult:
            # if item.exclude_from_nav:
            #     continue
            cid, item_url = _get_url(item)
            data = {
                'name': utils.pretty_title_or_id(context, item),
                'id': item.getId,
                'url': item_url,
                'description': item.Description,
                'review_state': item.review_state
            }
            result.append(data)

        return result


class PortletNavigation(object):
    """ Builds the tree for the navigation portlet serializer
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal = getSite()

    def __call__(self, depth, includeTop, currentFolderOnly):
        self.depth = depth
        result = {}

        # uses local context as "root" instead of default INavigationRoot
        tabs = CatalogNavigationTabs(self.context, self.request)
        items = []

        for tab in tabs.topLevelTabs(currentFolderOnly):
            if self.depth != 1:
                subitems = self.getTabSubTree(
                    tabUrl=tab["url"], tabPath=tab.get("path")
                )
                items.append(
                    {
                        "title": tab.get("title", tab.get("name")),
                        "@id": tab["url"] + "",
                        "description": tab.get("description", ""),
                        "items": subitems,
                    }
                )
            else:
                items.append(
                    {
                        "title": tab.get("title", tab.get("name")),
                        "@id": tab["url"] + "",
                        "description": tab.get("description", ""),
                    }
                )

        if includeTop:
            if utils.safe_hasattr(self.context, 'getRemoteUrl'):
                item_url = self.context.getRemoteUrl()
            else:
                cid, item_url = get_view_url(self.context)
            data = {
                'title': self.context.pretty_title_or_id(),
                'id': self.context.getId(),
                '@id': item_url,
                'description': self.context.Description(),
                # 'review_state': content.get_state(self.context)
            }
            items = [data] + items

        result["items"] = items

        return result

    def getTabSubTree(self, tabUrl="", tabPath=None):
        if tabPath is None:
            # get path for current tab's object
            tabPath = tabUrl.split(self.portal.absolute_url())[-1]

            if tabPath == "" or "/view" in tabPath:
                return ""

            if tabPath.startswith("/"):
                tabPath = tabPath[1:]
            elif tabPath.endswith("/"):
                # we need a real path, without a slash that might appear
                # at the end of the path occasionally
                tabPath = str(tabPath.split("/")[0])

            if "%20" in tabPath:
                # we have the space in object's ID that has to be
                # converted to the real spaces
                tabPath = tabPath.replace("%20", " ").strip()

        tabObj = self.portal.restrictedTraverse(tabPath, None)

        if tabObj is None:
            return ""

        strategy = CustomNavtreeStrategy(tabObj, self.depth)
        queryBuilder = NavigationTreeQueryBuilder(tabObj, self.depth)
        query = queryBuilder()
        data = buildFolderTree(
            tabObj, obj=tabObj, query=query, strategy=strategy)

        return self.recurse(children=data.get("children", []), level=1)

    def recurse(self, children=None, level=0, bottomLevel=0):
        li = []

        for node in children:
            item = {"title": node["Title"], "description": node["Description"]}
            item["@id"] = node["getURL"]

            if bottomLevel <= 0 or level <= bottomLevel:
                nc = node["children"]
                nc = self.recurse(nc, level + 1, bottomLevel)

                if nc:
                    item["items"] = nc
            li.append(item)

        return li
