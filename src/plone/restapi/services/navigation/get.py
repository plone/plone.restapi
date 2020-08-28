# -*- coding: utf-8 -*-
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.root import getNavigationRoot
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder
from Products.CMFPlone.browser.navtree import SitemapNavtreeStrategy
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface


class NavigationTreeQueryBuilder(NavtreeQueryBuilder):
    """Build a folder tree query"""

    def __init__(self, context, depth):
        NavtreeQueryBuilder.__init__(self, context)
        self.query["path"] = {
            "query": "/".join(context.getPhysicalPath()),
            "navtree_start": 1,
            "depth": depth - 1,
        }


class CustomNavtreeStrategy(SitemapNavtreeStrategy):
    """The navtree strategy used for the default navigation portlet"""

    def __init__(self, context):
        SitemapNavtreeStrategy.__init__(self, context, None)
        self.context = context
        self.bottomLevel = 0
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
        rootPath = getNavigationRoot(self.context)

        contextPath = "/".join(self.context.getPhysicalPath())
        if not contextPath.startswith(rootPath):
            return None
        contextSubPathElements = contextPath[len(rootPath) + 1 :]
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


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Navigation(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal = getSite()

    def __call__(self, expand=False):
        if self.request.form.get("expand.navigation.depth", False):
            self.depth = int(self.request.form["expand.navigation.depth"])
        else:
            self.depth = 1

        result = {
            "navigation": {"@id": "{}/@navigation".format(self.context.absolute_url())}
        }
        if not expand:
            return result

        tabs = getMultiAdapter((self.context, self.request), name="portal_tabs_view")
        items = []
        for tab in tabs.topLevelTabs():
            if self.depth > 1:
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
        result["navigation"]["items"] = items
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

        strategy = CustomNavtreeStrategy(tabObj)
        queryBuilder = NavigationTreeQueryBuilder(tabObj, self.depth)
        query = queryBuilder()
        data = buildFolderTree(tabObj, obj=tabObj, query=query, strategy=strategy)

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


class NavigationGet(Service):
    def reply(self):
        navigation = Navigation(self.context, self.request)
        return navigation(expand=True)["navigation"]
