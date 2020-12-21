# -*- coding: utf-8 -*-

""" A flexible navigation service that uses class navigation portlet semantics
"""

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from collections import namedtuple
from plone import api
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.uuid.utils import uuidToObject
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interfaces import IBrowserDefault
from Products.CMFPlone import utils
from Products.CMFPlone.defaultpage import is_default_page
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.interfaces import ISiteSchema
from Products.MimetypesRegistry.MimeTypeItem import guess_icon_path
from zExceptions import NotFound
from zope import schema
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer
from zope.interface import Interface

import os


_ = MessageFactory("plone.restapi")


class INavigationPortlet(Interface):
    """A portlet which can render the navigation tree"""

    name = schema.TextLine(
        title=_(u"label_navigation_title", default=u"Title"),
        description=_(
            u"help_navigation_title", default=u"The title of the navigation tree."
        ),
        default=u"",
        required=False,
    )

    root_path = schema.TextLine(
        title=_(u"label_navigation_root_path", default=u"Root node"),
        description=_(
            u"help_navigation_root",
            default=u"You may search for and choose a folder "
            "to act as the root of the navigation tree. "
            "Leave blank to use the Plone site root.",
        ),
        required=False,
    )

    includeTop = schema.Bool(
        title=_(u"label_include_top_node", default=u"Include top node"),
        description=_(
            u"help_include_top_node",
            default=u"Whether or not to show the top, or 'root', "
            "node in the navigation tree. This is affected "
            "by the 'Start level' setting.",
        ),
        default=False,
        required=False,
    )

    currentFolderOnly = schema.Bool(
        title=_(
            u"label_current_folder_only",
            default=u"Only show the contents of the current folder.",
        ),
        description=_(
            u"help_current_folder_only",
            default=u"If selected, the navigation tree will "
            "only show the current folder and its "
            "children at all times.",
        ),
        default=False,
        required=False,
    )

    topLevel = schema.Int(
        title=_(u"label_navigation_startlevel", default=u"Start level"),
        description=_(
            u"help_navigation_start_level",
            default=u"An integer value that specifies the number of folder "
            "levels below the site root that must be exceeded "
            "before the navigation tree will display. 0 means "
            "that the navigation tree should be displayed "
            "everywhere including pages in the root of the site. "
            "1 means the tree only shows up inside folders "
            "located in the root and downwards, never showing "
            "at the top level.",
        ),
        default=1,
        required=False,
    )

    bottomLevel = schema.Int(
        title=_(u"label_navigation_tree_depth", default=u"Navigation tree depth"),
        description=_(
            u"help_navigation_tree_depth",
            default=u"How many folders should be included "
            "before the navigation tree stops. 0 "
            "means no limit. 1 only includes the "
            "root folder.",
        ),
        default=0,
        required=False,
    )

    no_icons = schema.Bool(
        title=_(u"Suppress Icons"),
        description=_(u"If enabled, the portlet will not show document type icons."),
        required=True,
        default=False,
    )

    thumb_scale = schema.TextLine(
        title=_(u"Override thumb scale"),
        description=_(
            u"Enter a valid scale name"
            u" (see 'Image Handling' control panel) to override"
            u" (e.g. icon, tile, thumb, mini, preview, ... )."
            u" Leave empty to use default (see 'Site' control panel)."
        ),
        required=False,
        default=u"",
    )

    no_thumbs = schema.Bool(
        title=_(u"Suppress thumbs"),
        description=_(u"If enabled, the portlet will not show thumbs."),
        required=True,
        default=False,
    )


class NavPortletGet(Service):
    def reply(self):
        navigation = NavigationPortlet(self.context, self.request)
        return navigation(expand=True, prefix="")["navportlet"]


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class NavigationPortlet(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False, prefix="expand.navportlet."):
        result = {
            "navportlet": {"@id": "{}/@navportlet".format(self.context.absolute_url())}
        }
        if not expand:
            return result

        # 'context', 'request', 'view', 'manager', and 'data'
        # import pdb
        #
        # pdb.set_trace()
        data = extract_data(INavigationPortlet, self.request.form, prefix)
        renderer = NavigationPortletRenderer(self.context, self.request.form, data)
        return renderer.render()


class NavigationPortletRenderer(object):
    def __init__(self, context, request, data):

        self.urltool = getToolByName(context, "portal_url")

    def title(self):
        return self.data.name or self.data.title

    def hasName(self):
        return self.data.name

    @property
    def available(self):
        rootpath = self.getNavRootPath()
        if rootpath is None:
            return False

        if self.data.bottomLevel < 0:
            return True

        tree = self.getNavTree()
        return len(tree["children"]) > 0

    def include_top(self):
        return getattr(self.data, "includeTop", True)

    def navigation_root(self):
        return self.getNavRoot()

    def heading_link_target(self):
        """
        Get the href target where clicking the portlet header will take you.

        If this is a customized portlet with a custom root item set,
        we probably want to take the user to the custom root item instead
        of the sitemap of the navigation root.

        Plone does not have subsection sitemaps so there is no point of
        displaying /sitemap links for anything besides nav root.
        """

        if not self.data.root_uid and not self.data.currentFolderOnly:
            # No particular root item assigned -> should get link to the
            # navigation root sitemap of the current context acquisition chain
            portal_state = getMultiAdapter(
                (self.context, self.request), name="plone_portal_state"
            )
            return portal_state.navigation_root_url() + "/sitemap"

        nav_root = self.getNavRoot()

        # Root content item gone away or similar issue
        if not nav_root:
            return None

        if INavigationRoot.providedBy(nav_root) or ISiteRoot.providedBy(nav_root):
            # For top level folders go to the sitemap
            return nav_root.absolute_url() + "/sitemap"
        else:
            # Go to the item /view we have chosen as root item
            return nav_root.absolute_url()

    def root_type_name(self):
        root = self.getNavRoot()
        return queryUtility(IIDNormalizer).normalize(root.portal_type)

    def root_item_class(self):
        context = aq_inner(self.context)
        root = self.getNavRoot()
        container = aq_parent(context)
        if aq_base(root) is aq_base(context) or (
            aq_base(root) is aq_base(container) and is_default_page(container, context)
        ):
            return "navTreeCurrentItem"
        return ""

    def root_is_portal(self):
        root = self.getNavRoot()
        return aq_base(root) is aq_base(self.urltool.getPortalObject())

    def createNavTree(self):
        data = self.getNavTree()

        bottomLevel = self.data.bottomLevel or 0

        if bottomLevel < 0:
            # Special case where navigation tree depth is negative
            # meaning that the admin does not want the listing to be displayed
            return self.recurse([], level=1, bottomLevel=bottomLevel)
        else:
            return self.recurse(
                children=data.get("children", []), level=1, bottomLevel=bottomLevel
            )

    # Cached lookups

    @memoize
    def getNavRootPath(self):
        return getRootPath(
            self.context,
            self.data.currentFolderOnly,
            self.data.topLevel,
            self.data.root_uid,
        )

    @memoize
    def getNavRoot(self, _marker=None):
        if _marker is None:
            _marker = []
        portal = self.urltool.getPortalObject()
        rootPath = self.getNavRootPath()
        if rootPath is None:
            return None

        if rootPath == self.urltool.getPortalPath():
            return portal
        else:
            try:
                return portal.unrestrictedTraverse(rootPath)
            except (AttributeError, KeyError, TypeError, NotFound):
                # TypeError: object is unsubscribtable might be
                # risen in some cases
                return portal

    @memoize
    def getNavTree(self, _marker=None):
        if _marker is None:
            _marker = []
        context = aq_inner(self.context)
        queryBuilder = getMultiAdapter((context, self.data), INavigationQueryBuilder)
        strategy = getMultiAdapter((context, self.data), INavtreeStrategy)

        return buildFolderTree(
            context, obj=context, query=queryBuilder(), strategy=strategy
        )

    @memoize
    def thumb_scale(self):
        """Use override value or read thumb_scale from registry.
        Image sizes must fit to value in allowed image sizes.
        None will suppress thumb.
        """
        if getattr(self.data, "no_thumbs", False):
            # Individual setting overrides
            return None
        thsize = getattr(self.data, "thumb_scale", None)
        if thsize:
            return thsize
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
        if settings.no_thumbs_portlet:
            return "none"
        thumb_scale_portlet = settings.thumb_scale_portlet
        return thumb_scale_portlet

    def getMimeTypeIcon(self, node):
        try:
            if not node["normalized_portal_type"] == "file":
                return None
            fileo = node["item"].getObject().file
            portal_url = getNavigationRoot(self.context)
            mtt = getToolByName(self.context, "mimetypes_registry")
            if fileo.contentType:
                ctype = mtt.lookup(fileo.contentType)
                return os.path.join(portal_url, guess_icon_path(ctype[0]))
        except AttributeError:
            return None
        return None

    def render(self):
        res = {
            "title": self.title(),
            "url": self.heading_link_target(),
            "has_custom_name": bool(self.hasName()),
            "items": [],
        }

        if self.include_top():
            root = self.navigation_root()
            root_is_portal = self.root_is_portal()

            if root is None:
                root = self.urltool.getPortalObject()
                root_is_portal = True

            if utils.safe_hasattr(self.context, "getRemoteUrl"):
                root_url = root.getRemoteUrl()
            else:
                # cid, root_url = get_view_url(root)
                # cid = get_id(root)
                root_url = get_url(root)

            root_title = "Home" if root_is_portal else root.pretty_title_or_id()
            root_type = (
                "plone-site"
                if root_is_portal
                else utils.normalizeString(root.portal_type, context=root)
            )
            normalized_id = utils.normalizeString(root.Title(), context=root)

            if root_is_portal:
                state = ""
            else:
                state = api.content.get_state(root)

            res["items"].append(
                {
                    "@id": root.absolute_url(),
                    "description": root.Description() or "",
                    "href": root_url,
                    "icon": "",
                    "is_current": bool(self.root_item_class()),
                    "is_folderish": True,
                    "is_in_path": True,
                    "items": [],
                    "normalized_id": normalized_id,
                    "thumb": "",
                    "title": root_title,
                    "type": root_type,
                    "review_state": state,
                }
            )

        res["items"].extend(self.createNavTree())

        return res

    def recurse(self, children, level, bottomLevel):
        # TODO: we should avoid recursion. This is just a rewrite of the TAL
        # template, but ideally we should use a dequeue structure to avoid
        # recursion problems.

        res = []

        show_thumbs = not self.data.no_thumbs
        show_icons = not self.data.no_icons

        thumb_scale = self.thumb_scale()

        for node in children:
            brain = node["item"]

            icon = ""

            if show_icons:
                if node["portal_type"] == "File":
                    icon = self.getMimeTypeIcon(node)

            has_thumb = brain.getIcon
            thumb = ""

            if show_thumbs and has_thumb and thumb_scale:
                thumb = "{}/@@images/image/{}".format(
                    node["item"].getURL(), thumb_scale
                )

            show_children = node["show_children"]
            item_remote_url = node["getRemoteUrl"]
            use_remote_url = node["useRemoteUrl"]
            item_url = node["getURL"]
            item = {
                "@id": item_url,
                "description": node["Description"],
                "href": item_remote_url if use_remote_url else item_url,
                "icon": icon,
                "is_current": node["currentItem"],
                "is_folderish": node["show_children"],
                "is_in_path": node["currentParent"],
                "items": [],
                "normalized_id": node["normalized_id"],
                "review_state": node["review_state"] or "",
                "thumb": thumb,
                "title": node["Title"],
                "type": node["normalized_portal_type"],
            }

            nodechildren = node["children"]

            if (
                nodechildren
                and show_children
                and ((bottomLevel < level) or (bottomLevel == 0))
            ):
                item["items"] = self.recurse(
                    nodechildren, level=level + 1, bottomLevel=bottomLevel
                )

            res.append(item)

        return res


def get_url(item):
    if not item:
        return None

    if hasattr(aq_base(item), "getURL"):
        # Looks like a brain

        return item.getURL()

    return item.absolute_url()


def get_id(item):
    if not item:
        return None
    getId = getattr(item, "getId")

    if not utils.safe_callable(getId):
        # Looks like a brain

        return getId

    return getId()


def get_view_url(context):
    registry = getUtility(IRegistry)
    view_action_types = registry.get("plone.types_use_view_action_in_listings", [])
    item_url = get_url(context)
    name = get_id(context)

    if getattr(context, "portal_type", {}) in view_action_types:
        item_url += "/view"
        name += "/view"

    return name, item_url


def getRootPath(context, currentFolderOnly, topLevel, root):
    """Helper function to calculate the real root path"""
    context = aq_inner(context)
    if currentFolderOnly:
        folderish = getattr(
            aq_base(context), "isPrincipiaFolderish", False
        ) and not INonStructuralFolder.providedBy(context)
        parent = aq_parent(context)

        is_default_page = False
        browser_default = IBrowserDefault(parent, None)
        if browser_default is not None:
            is_default_page = browser_default.getDefaultPage() == context.getId()

        if not folderish or is_default_page:
            return "/".join(parent.getPhysicalPath())
        else:
            return "/".join(context.getPhysicalPath())

    root = uuidToObject(root)
    if root is not None:
        rootPath = "/".join(root.getPhysicalPath())
    else:
        rootPath = getNavigationRoot(context)

    # Adjust for topLevel
    if topLevel > 0:
        contextPath = "/".join(context.getPhysicalPath())
        if not contextPath.startswith(rootPath):
            return None
        contextSubPathElements = contextPath[len(rootPath) + 1 :]
        if contextSubPathElements:
            contextSubPathElements = contextSubPathElements.split("/")
            if len(contextSubPathElements) < topLevel:
                return None
            rootPath = rootPath + "/" + "/".join(contextSubPathElements[:topLevel])
        else:
            return None

    return rootPath


def extract_data(schema, raw_data, prefix):
    data = namedtuple("Data", schema.names())
    for name in schema.names():
        setattr(data, name, raw_data.get(prefix + name, schema[name].default))

    return data


# from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
# from Products.CMFPlone.interfaces import INavigationSchema
# from zope import schema
# from zope.component import adapts
# from Acquisition import aq_base
# from ComputedAttribute import ComputedAttribute
# from plone.app.layout.navigation.root import getNavigationRootObject
# from plone.app.portlets import PloneMessageFactory as _
# from plone.app.portlets.portlets import base
# from plone.app.vocabularies.catalog import CatalogSource
# from plone.portlets.interfaces import IPortletDataProvider
# from plone.registry.interfaces import IRegistry
# from Products.CMFPlone import utils
# from zope.component import getUtility
# from zope.interface import implementer
# from zope.interface import Interface
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from plone.restapi.deserializer import json_body
