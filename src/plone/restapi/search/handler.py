from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import IZCatalogCompatibleQuery
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.interfaces import ISearchSchema
from zope.component import getMultiAdapter
from zope.component import getUtility


class SearchHandler:
    """Executes a catalog search based on a query dict, and returns
    JSON compatible results.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.catalog = getToolByName(self.context, "portal_catalog")

    def _parse_query(self, query):
        catalog_compatible_query = getMultiAdapter(
            (self.context, self.request), IZCatalogCompatibleQuery
        )(query)
        return catalog_compatible_query

    def _constrain_query_by_path(self, query):
        """If no 'path' query was supplied, restrict search to current
        context and its children by adding a path constraint.

        The following cases can happen here:
        - No 'path' parameter at all
        - 'path' query dict with options, but no actual 'query' inside
        - 'path' supplied as a string
        - 'path' supplied as a complete query dict
        """
        if "path" not in query:
            query["path"] = {}

        if isinstance(query["path"], str) or isinstance(query["path"], list):
            query["path"] = {"query": query["path"]}

        # If this is accessed through a VHM the client does not know
        # the complete physical path of an object. But the path index
        # indexes the complete physical path. Complete the path.
        vhm_physical_path = self.request.get("VirtualRootPhysicalPath")
        if vhm_physical_path:
            path = query["path"].get("query")
            if path:
                if isinstance(path, str):
                    path = path.lstrip("/")
                    full_path = "/".join(vhm_physical_path + (path,))
                    query["path"]["query"] = full_path
                if isinstance(path, list):
                    full_paths = []
                    for p in path:
                        p = p.lstrip("/")
                        full_path = "/".join(vhm_physical_path + (p,))
                        full_paths.append(full_path)
                    query["path"]["query"] = full_paths

        if isinstance(query["path"], dict) and "query" not in query["path"]:
            # We either had no 'path' parameter at all, or an incomplete
            # 'path' query dict (with just ExtendedPathIndex options (like
            # 'depth'), but no actual path 'query' in it).
            #
            # In either case, we'll prefill with the context's path
            path = "/".join(self.context.getPhysicalPath())
            query["path"]["query"] = path

    def search(self, query=None):
        if query is None:
            query = {}
        if "fullobjects" in query:
            fullobjects = True
            del query["fullobjects"]
        else:
            fullobjects = False

        use_site_search_settings = False

        if "use_site_search_settings" in query:
            use_site_search_settings = True
            del query["use_site_search_settings"]

        if use_site_search_settings:
            query = self.filter_query(query)

        self._constrain_query_by_path(query)
        query = self._parse_query(query)

        lazy_resultset = self.catalog.searchResults(**query)
        results = getMultiAdapter((lazy_resultset, self.request), ISerializeToJson)(
            fullobjects=fullobjects
        )

        return results

    def filter_types(self, types):
        plone_utils = getToolByName(self.context, "plone_utils")
        if not isinstance(types, list):
            types = [types]
        return plone_utils.getUserFriendlyTypes(types)

    def filter_query(self, query):
        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix="plone")

        types = query.get("portal_type", [])
        if "query" in types:
            types = types["query"]
        query["portal_type"] = self.filter_types(types)

        # respect effective/expiration date
        query["show_inactive"] = False

        # respect navigation root
        if "path" not in query:
            query["path"] = {"query": getNavigationRoot(self.context)}

            vhm_physical_path = self.request.get("VirtualRootPhysicalPath")
            # if vhm trick is applied, we should present a stripped path, as it will be
            # processed again in _constrain_query_by_path
            if vhm_physical_path:
                bits = query["path"]["query"].split("/")[len(vhm_physical_path) :]
                query["path"]["query"] = "/".join(bits) or "/"

        default_sort_on = search_settings.sort_on

        if "sort_on" not in query:
            if default_sort_on != "relevance":
                query["sort_on"] = self.default_sort_on
        elif query["sort_on"] == "relevance":
            del query["sort_on"]

        if not query.get("sort_order") and (
            query.get("sort_on", "") == "Date"
            or query.get("sort_on", "") == "effective"  # compatibility with Volto
        ):
            query["sort_order"] = "reverse"
        elif "sort_order" in query:
            del query["sort_order"]

        if "sort_order" in query and not query["sort_order"]:
            del query["sort_order"]

        return query
