"""A flexible navigation service that uses class navigation portlet semantics"""

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from collections import UserDict
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from plone.restapi.bbb import check_default_page_via_view
from plone.restapi.bbb import get_navigation_root
from plone.restapi.bbb import INavigationRoot
from plone.restapi.bbb import INavigationSchema
from plone.restapi.bbb import INonStructuralFolder
from plone.restapi.bbb import is_default_page
from plone.restapi.bbb import ISiteSchema
from plone.restapi.bbb import safe_callable
from plone.restapi.bbb import safe_hasattr
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.interfaces import IBrowserDefault
from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from Products.CMFPlone.utils import normalizeString
from Products.CMFPlone.utils import typesToList
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
from zope.schema.interfaces import IFromUnicode

import os

_ = MessageFactory("plone.restapi")


class INavigationPortlet(Interface):
    """A portlet which can render the navigation tree"""

    name = schema.TextLine(
        title=_("label_navigation_title", default="Title"),
        description=_(
            "help_navigation_title", default="The title of the navigation tree."
        ),
        default="",
        required=False,
    )

    root_path = schema.TextLine(
        title=_("label_navigation_root_path", default="Root node"),
        description=_(
            "help_navigation_root",
            default="You may search for and choose a folder "
            "to act as the root of the navigation tree. "
            "Leave blank to use the Plone site root.",
        ),
        required=False,
    )

    includeTop = schema.Bool(
        title=_("label_include_top_node", default="Include top node"),
        description=_(
            "help_include_top_node",
            default="Whether or not to show the top, or 'root', "
            "node in the navigation tree. This is affected "
            "by the 'Start level' setting.",
        ),
        default=False,
        required=False,
    )

    currentFolderOnly = schema.Bool(
        title=_(
            "label_current_folder_only",
            default="Only show the contents of the current folder.",
        ),
        description=_(
            "help_current_folder_only",
            default="If selected, the navigation tree will "
            "only show the current folder and its "
            "children at all times.",
        ),
        default=False,
        required=False,
    )

    topLevel = schema.Int(
        title=_("label_navigation_startlevel", default="Start level"),
        description=_(
            "help_navigation_start_level",
            default="An integer value that specifies the number of folder "
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
        title=_("label_navigation_tree_depth", default="Navigation tree depth"),
        description=_(
            "help_navigation_tree_depth",
            default="How many folders should be included "
            "before the navigation tree stops. 0 "
            "means no limit. 1 only includes the "
            "root folder.",
        ),
        default=0,
        required=False,
    )

    no_icons = schema.Bool(
        title=_("Suppress Icons"),
        description=_("If enabled, the portlet will not show document type icons."),
        required=True,
        default=False,
    )

    thumb_scale = schema.TextLine(
        title=_("Override thumb scale"),
        description=_(
            "Enter a valid scale name"
            " (see 'Image Handling' control panel) to override"
            " (e.g. icon, tile, thumb, mini, preview, ... )."
            " Leave empty to use default (see 'Site' control panel)."
        ),
        required=False,
        default="",
    )

    no_thumbs = schema.Bool(
        title=_("Suppress thumbs"),
        description=_("If enabled, the portlet will not show thumbs."),
        required=True,
        default=False,
    )


class ContextNavigationGet(Service):
    def reply(self):
        navigation = ContextNavigation(self.context, self.request)
        return navigation(expand=True, prefix="expand.contextnavigation.")[
            "contextnavigation"
        ]


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class ContextNavigation:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False, prefix="expand.contextnavigation."):
        result = {
            "contextnavigation": {
                "@id": f"{self.context.absolute_url()}/@contextnavigation"
            }
        }
        if not expand:
            return result

        data = extract_data(INavigationPortlet, self.request.form, prefix)
        renderer = NavigationPortletRenderer(self.context, self.request, data)
        res = renderer.render()
        result["contextnavigation"].update(res)
        return result

    def getNavTree(self):
        # compatibility method with NavigationPortletRenderer, only for tests
        return self.__call__(expand=True)["contextnavigation"]


class NavigationPortletRenderer:
    def __init__(self, context, request, data):
        self.context = context
        self.request = request
        self.data = data
        self.urltool = getToolByName(context, "portal_url")

    def title(self):
        return self.data.name or self.data.title or _("Navigation")

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

        if not self.data.root_path and not self.data.currentFolderOnly:
            # No particular root item assigned -> should get link to the
            # navigation root sitemap of the current context acquisition chain
            portal_state = getMultiAdapter(
                (self.context, self.request), name="plone_portal_state"
            )
            return portal_state.navigation_root_url() + "/sitemap"

        nav_root = self.getNavRoot()

        # Root content item gone away or similar issue
        if not nav_root:
            return

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
        is_default = is_default_page(container, context)
        if aq_base(root) is aq_base(context) or (
            aq_base(root) is aq_base(container) and is_default
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
            self.data.root_path,
        )

    @memoize
    def getNavRoot(self, _marker=None):
        if _marker is None:
            _marker = []
        portal = self.urltool.getPortalObject()
        rootPath = self.getNavRootPath()
        if rootPath is None:
            return

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
        queryBuilder = QueryBuilder(context, self.data)
        strategy = NavtreeStrategy(context, self.data)

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
            return
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
                return
            fileo = node["item"].getObject().file
            portal_url = get_navigation_root(self.context)
            mtt = getToolByName(self.context, "mimetypes_registry")
            if fileo.contentType:
                ctype = mtt.lookup(fileo.contentType)
                if ctype:
                    return os.path.join(portal_url, guess_icon_path(ctype[0]))
        except AttributeError:
            pass

    def render(self):
        res = {
            "title": self.title(),
            "url": self.heading_link_target(),
            "has_custom_name": bool(self.hasName()),
            "items": [],
            "available": self.available,
        }
        if not res["available"]:
            return res

        if self.include_top():
            root = self.navigation_root()
            root_is_portal = self.root_is_portal()

            if root is None:
                root = self.urltool.getPortalObject()
                root_is_portal = True

            if safe_hasattr(self.context, "getRemoteUrl"):
                root_url = root.getRemoteUrl()
            else:
                # cid, root_url = get_view_url(root)
                # cid = get_id(root)
                root_url = get_url(root)

            root_title = "Home" if root_is_portal else root.pretty_title_or_id()
            root_type = (
                "plone-site"
                if root_is_portal
                else normalizeString(root.portal_type, context=root)
            )
            normalized_id = normalizeString(root.Title(), context=root)

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

            if node.get("nav_title", False):
                item.update({"title": node["nav_title"]})

            nodechildren = node["children"]

            if (
                nodechildren
                and show_children
                and ((level < bottomLevel) or (bottomLevel == 0))
            ):
                item["items"] = self.recurse(
                    nodechildren, level=level + 1, bottomLevel=bottomLevel
                )

            res.append(item)

        return res


def get_url(item):
    if not item:
        return

    if hasattr(aq_base(item), "getURL"):
        # Looks like a brain

        return item.getURL()

    return item.absolute_url()


def get_id(item):
    if not item:
        return
    getId = getattr(item, "getId")

    if not safe_callable(getId):
        # Looks like a brain

        return getId

    return getId()


def get_view_url(context):
    registry = getUtility(IRegistry)
    view_action_types = registry.get("plone.types_use_view_action_in_listings", [])
    item_url = get_url(context)
    name = get_id(context)

    if getattr(context, "portal_type", {}) in view_action_types:
        item_url += "/view"  # TODO: don't need this
        name += "/view"

    return name, item_url


def _is_default_page(container, context):
    is_default_page = False
    browser_default = IBrowserDefault(container, None)
    if browser_default is not None:
        is_default_page = browser_default.getDefaultPage() == context.getId()

    return is_default_page


def getRootPath(context, currentFolderOnly, topLevel, root_path):
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

    # root = uuidToObject(root)
    root = get_root(context, root_path)

    if root is not None:
        rootPath = "/".join(root.getPhysicalPath())
    else:
        rootPath = get_navigation_root(context)

    # Adjust for topLevel
    if topLevel > 0:
        contextPath = "/".join(context.getPhysicalPath())
        if not contextPath.startswith(rootPath):
            return
        contextSubPathElements = contextPath[len(rootPath) + 1 :]
        if contextSubPathElements:
            contextSubPathElements = contextSubPathElements.split("/")
            if len(contextSubPathElements) < topLevel:
                return
            rootPath = rootPath + "/" + "/".join(contextSubPathElements[:topLevel])
        else:
            return

    return rootPath


class Data(UserDict):
    def __getattr__(self, name):
        return self.data.get(name, None)


def extract_data(schema, raw_data, prefix):
    data = Data({})

    for name in schema.names():
        field = schema[name]
        raw_value = raw_data.get(prefix + name, field.default)

        value = IFromUnicode(field).fromUnicode(raw_value)
        data[name] = value  # convert(raw_value, field)

    return data


def get_root(context, root_path):
    if root_path is None:
        return

    urltool = getToolByName(context, "portal_url")
    portal = urltool.getPortalObject()
    if root_path.startswith("/"):
        root_path = root_path[1:]
    try:
        root = context.restrictedTraverse(
            portal.getPhysicalPath() + tuple(root_path.split("/"))
        )
    except (IndexError, KeyError):
        return portal
    return root


class QueryBuilder:
    """Build a navtree query based on the settings in INavigationSchema
    and those set on the portlet.
    """

    def __init__(self, context, data):
        self.context = context
        self.data = data

        # Acquire a custom nav query if available
        customQuery = getattr(context, "getCustomNavQuery", None)
        if customQuery is not None and safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        # Construct the path query
        root = get_root(context, data.root_path)
        if root is not None:
            rootPath = "/".join(root.getPhysicalPath())
        else:
            rootPath = get_navigation_root(context)

        currentPath = "/".join(context.getPhysicalPath())

        # If we are above the navigation root, a navtree query would return
        # nothing (since we explicitly start from the root always). Hence,
        # use a regular depth-1 query in this case.

        depth = data.bottomLevel

        if depth == 0:
            depth = 999

        if currentPath != rootPath and not currentPath.startswith(rootPath + "/"):
            query["path"] = {"query": rootPath, "depth": depth}
        else:
            query["path"] = {"query": currentPath, "depth": depth, "navtree": 1}

        topLevel = data.topLevel
        if topLevel and topLevel > 0:
            query["path"]["navtree_start"] = topLevel + 1

        # XXX: It'd make sense to use 'depth' for bottomLevel, but it doesn't
        # seem to work with EPI.

        # Only list the applicable types
        query["portal_type"] = typesToList(context)

        # Filter on workflow states, if enabled
        registry = getUtility(IRegistry)
        navigation_settings = registry.forInterface(INavigationSchema, prefix="plone")
        if navigation_settings.filter_on_workflow:
            query["review_state"] = navigation_settings.workflow_states_to_show

        self.query = query

    def __call__(self):
        return self.query


class NavtreeStrategy(SitemapNavtreeStrategy):
    """The navtree strategy used for the default navigation portlet"""

    def __init__(self, context, portlet):
        SitemapNavtreeStrategy.__init__(self, context, portlet)

        # XXX: We can't do this with a 'depth' query to EPI...
        self.bottomLevel = portlet.bottomLevel or 0

        self.rootPath = getRootPath(
            context, portlet.currentFolderOnly, portlet.topLevel, portlet.root_path
        )

    def subtreeFilter(self, node):
        sitemapDecision = SitemapNavtreeStrategy.subtreeFilter(self, node)
        if sitemapDecision is False:
            return False
        depth = node.get("depth", 0)
        if depth > 0 and self.bottomLevel > 0 and depth >= self.bottomLevel:
            return False
        else:
            return True

    def decoratorFactory(self, node):
        new_node = SitemapNavtreeStrategy.decoratorFactory(self, node)
        if getattr(new_node["item"], "nav_title", False):
            new_node["nav_title"] = new_node["item"].nav_title
        return new_node


def buildFolderTree(context, obj=None, query={}, strategy=None):
    """Create a tree structure representing a navigation tree. By default,
    it will create a full "sitemap" tree, rooted at the portal, ordered
    by explicit folder order. If the 'query' parameter contains a 'path'
    key, this can be used to override this. To create a navtree rooted
    at the portal root, set query['path'] to:

        {'query' : '/'.join(context.getPhysicalPath()),
         'navtree' : 1}

    to start this 1 level below the portal root, set query['path'] to:

        {'query' : '/'.join(obj.getPhysicalPath()),
         'navtree' : 1,
         'navtree_start' : 1}

    to create a sitemap with depth limit 3, rooted in the portal:

        {'query' : '/'.join(obj.getPhysicalPath()),
         'depth' : 3}

    The parameters:

    - 'context' is the acquisition context, from which tools will be acquired
    - 'obj' is the current object being displayed.
    - 'query' is a catalog query to apply to find nodes in the tree.
    - 'strategy' is an object that can affect how the generation works. It
        should be derived from NavtreeStrategyBase, if given, and contain:

            rootPath -- a string property; the physical path to the root node.

            If not given, it will default to any path set in the query, or the
            portal root. Note that in a navtree query, the root path will
            default to the portal only, possibly adjusted for any navtree_start
            set. If rootPath points to something not returned by the query by
            the query, a dummy node containing only an empty 'children' list
            will be returned.

            showAllParents -- a boolean property; if true and obj is given,
                ensure that all parents of the object, including any that would
                normally be filtered out are included in the tree.

            supplimentQuery -- a dictionary property; provides
                additional query terms which, if not already present
                in the query, are added.  Useful, for example, to
                affect default sorting or default page behavior.

            nodeFilter(node) -- a method returning a boolean; if this returns
                False, the given node will not be inserted in the tree

            subtreeFilter(node) -- a method returning a boolean; if this
                returns False, the given (folderish) node will not be expanded
                (its children will be pruned off)

            decoratorFactory(node) -- a method returning a dict; this can
                inject additional keys in a node being inserted.

            showChildrenOf(object) -- a method returning True if children of
                the given object (normally the root) should be returned

    Returns tree where each node is represented by a dict:

        item            -   A catalog brain of this item
        depth           -   The depth of this item, relative to the startAt
                            level
        currentItem     -   True if this is the current item
        currentParent   -   True if this is a direct parent of the current item
        children        -   A list of children nodes of this node

    Note: Any 'decoratorFactory' specified may modify this list, but
    the 'children' property is guaranteed to be there.

    Note: If the query does not return the root node itself, the root
    element of the tree may contain *only* the 'children' list.

    Note: Folder default-pages are not included in the returned result.
    If the 'obj' passed in is a default-page, its parent folder will be
    used for the purposes of selecting the 'currentItem'.
    """

    portal_url = getToolByName(context, "portal_url")
    portal_catalog = getToolByName(context, "portal_catalog")

    rootPath = strategy.rootPath

    request = getattr(context, "REQUEST", {})

    # Find the object's path. Use parent folder if context is a default-page

    objPath = None
    objPhysicalPath = None
    if obj is not None:
        objPhysicalPath = obj.getPhysicalPath()
        if check_default_page_via_view(obj, request):
            objPhysicalPath = objPhysicalPath[:-1]
        objPath = "/".join(objPhysicalPath)

    portalPath = portal_url.getPortalPath()
    portalObject = portal_url.getPortalObject()

    # Calculate rootPath from the path query if not set.

    if "path" not in query:
        if rootPath is None:
            rootPath = portalPath
        query["path"] = rootPath
    elif rootPath is None:
        pathQuery = query["path"]
        if isinstance(pathQuery, str):
            rootPath = pathQuery
        else:
            # Adjust for the fact that in a 'navtree' query, the actual path
            # is the path of the current context
            if pathQuery.get("navtree", False):
                navtreeLevel = pathQuery.get("navtree_start", 1)
                if navtreeLevel > 1:
                    navtreeContextPath = pathQuery["query"]
                    navtreeContextPathElements = navtreeContextPath[
                        len(portalPath) + 1 :
                    ].split("/")
                    # Short-circuit if we won't be able to find this path
                    if len(navtreeContextPathElements) < (navtreeLevel - 1):
                        return {"children": []}
                    rootPath = (
                        portalPath
                        + "/"
                        + "/".join(navtreeContextPathElements[: navtreeLevel - 1])
                    )
                else:
                    rootPath = portalPath
            else:
                rootPath = pathQuery["query"]

    rootDepth = len(rootPath.split("/"))

    # Determine if we need to prune the root (but still force the path to)
    # the parent if necessary

    pruneRoot = False
    if strategy is not None:
        rootObject = portalObject.unrestrictedTraverse(rootPath, None)
        if rootObject is not None:
            pruneRoot = not strategy.showChildrenOf(rootObject)

    # Allow the strategy to supplement the query for keys not already
    # present in the query such as sorting and omitting default pages
    for key, value in strategy.supplimentQuery.items():
        if key not in query:
            query[key] = value

    results = portal_catalog.searchResults(query)

    # We keep track of a dict of item path -> node, so that we can easily
    # find parents and attach children. If a child appears before its
    # parent, we stub the parent node.

    # This is necessary because whilst the sort_on parameter will ensure
    # that the objects in a folder are returned in the right order relative
    # to each other, we don't know the relative order of objects from
    # different folders. So, if /foo comes before /bar, and /foo/a comes
    # before /foo/b, we may get a list like (/bar/x, /foo/a, /foo/b, /foo,
    # /bar,).

    itemPaths = {}

    # Add an (initially empty) node for the root
    itemPaths[rootPath] = {"children": []}

    # If we need to "prune" the parent (but still allow showAllParent to
    # force some children), do so now
    if pruneRoot:
        itemPaths[rootPath]["_pruneSubtree"] = True

    def insertElement(itemPaths, item, forceInsert=False):
        """Insert the given 'item' brain into the tree, which is kept in
        'itemPaths'. If 'forceInsert' is True, ignore node- and subtree-
        filters, otherwise any node- or subtree-filter set will be allowed to
        block the insertion of a node.
        """
        itemPath = item.getPath()
        itemInserted = itemPaths.get(itemPath, {}).get("item", None) is not None

        # Short-circuit if we already added this item. Don't short-circuit
        # if we're forcing the insert, because we may have inserted but
        # later pruned off the node
        if not forceInsert and itemInserted:
            return

        itemPhysicalPath = itemPath.split("/")
        parentPath = "/".join(itemPhysicalPath[:-1])
        parentPruned = itemPaths.get(parentPath, {}).get("_pruneSubtree", False)

        # Short-circuit if we know we're pruning this item's parent

        # XXX: We could do this recursively, in case of parent of the
        # parent was being pruned, but this may not be a great trade-off

        # There is scope for more efficiency improvement here: If we knew we
        # were going to prune the subtree, we would short-circuit here each
        # time. In order to know that, we'd have to make sure we inserted each
        # parent before its children, by sorting the catalog result set
        # (probably manually) to get a breadth-first search.

        if not forceInsert and parentPruned:
            return

        isCurrent = isCurrentParent = False
        if objPath is not None:
            objpath_startswith_itempath = objPath.startswith(itemPath + "/")
            objpath_bigger_than_itempath = len(objPhysicalPath) > len(itemPhysicalPath)
            if objPath == itemPath:
                isCurrent = True
            elif objpath_startswith_itempath and objpath_bigger_than_itempath:
                isCurrentParent = True

        relativeDepth = len(itemPhysicalPath) - rootDepth

        newNode = {
            "item": item,
            "depth": relativeDepth,
            "currentItem": isCurrent,
            "currentParent": isCurrentParent,
        }

        insert = True
        if not forceInsert and strategy is not None:
            insert = strategy.nodeFilter(newNode)
        if insert:
            if strategy is not None:
                newNode = strategy.decoratorFactory(newNode)

            # Tell parent about this item, unless an earlier subtree filter
            # told us not to. If we're forcing the insert, ignore the
            # pruning, but avoid inserting the node twice
            if parentPath in itemPaths:
                itemParent = itemPaths[parentPath]
                if forceInsert:
                    nodeAlreadyInserted = False
                    for i in itemParent["children"]:
                        if i["item"].getPath() == itemPath:
                            nodeAlreadyInserted = True
                            break
                    if not nodeAlreadyInserted:
                        itemParent["children"].append(newNode)
                elif not itemParent.get("_pruneSubtree", False):
                    itemParent["children"].append(newNode)
            else:
                itemPaths[parentPath] = {"children": [newNode]}

            # Ask the subtree filter (if any), if we should be expanding this
            # node
            if strategy.showAllParents and isCurrentParent:
                # If we will be expanding this later, we can't prune off
                # children now
                expand = True
            else:
                expand = getattr(item, "is_folderish", True)
            if expand and (not forceInsert and strategy is not None):
                expand = strategy.subtreeFilter(newNode)

            children = newNode.setdefault("children", [])
            if expand:
                # If we had some orphaned children for this node, attach
                # them
                if itemPath in itemPaths:
                    children.extend(itemPaths[itemPath]["children"])
            else:
                newNode["_pruneSubtree"] = True

            itemPaths[itemPath] = newNode

    # Add the results of running the query
    for r in results:
        insertElement(itemPaths, r)

    # If needed, inject additional nodes for the direct parents of the
    # context. Note that we use an unrestricted query: things we don't normally
    # have permission to see will be included in the tree.
    if strategy.showAllParents and objPath is not None:
        objSubPathElements = objPath[len(rootPath) + 1 :].split("/")
        parentPaths = []

        haveNode = itemPaths.get(rootPath, {}).get("item", None) is None
        if not haveNode:
            parentPaths.append(rootPath)

        parentPath = rootPath
        for i in range(len(objSubPathElements)):
            nodePath = rootPath + "/" + "/".join(objSubPathElements[: i + 1])
            node = itemPaths.get(nodePath, None)

            # If we don't have this node, we'll have to get it, if we have it
            # but it wasn't connected, re-connect it
            if node is None or "item" not in node:
                parentPaths.append(nodePath)
            else:
                nodeParent = itemPaths.get(parentPath, None)
                if nodeParent is not None:
                    nodeAlreadyInserted = False
                    for i in nodeParent["children"]:
                        if i["item"].getPath() == nodePath:
                            nodeAlreadyInserted = True
                            break
                    if not nodeAlreadyInserted:
                        nodeParent["children"].append(node)

            parentPath = nodePath

        # If we were outright missing some nodes, find them again
        if len(parentPaths) > 0:
            query = {"path": {"query": parentPaths, "depth": 0}}
            results = portal_catalog.unrestrictedSearchResults(query)

            for r in results:
                insertElement(itemPaths, r, forceInsert=True)

    # Return the tree starting at rootPath as the root node.
    return itemPaths[rootPath]
