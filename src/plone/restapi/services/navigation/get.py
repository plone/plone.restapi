from Acquisition import aq_inner
from collections import defaultdict
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from plone.registry.interfaces import IRegistry
from plone.restapi.bbb import get_navigation_root
from plone.restapi.bbb import INavigationSchema
from plone.restapi.bbb import safe_text
from plone.restapi.deserializer import parse_int
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Navigation:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal = getSite()

    def __call__(self, expand=False):
        self.depth = parse_int(self.request.form, "expand.navigation.depth", 1)

        result = {"navigation": {"@id": f"{self.context.absolute_url()}/@navigation"}}
        if not expand:
            return result

        result["navigation"]["items"] = self.build_tree(self.navtree_path)
        return result

    @property
    @memoize_contextless
    def settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(INavigationSchema, prefix="plone")
        return {
            "displayed_types": settings.displayed_types,
            "nonfolderish_tabs": settings.nonfolderish_tabs,
            "filter_on_workflow": settings.filter_on_workflow,
            "workflow_states_to_show": settings.workflow_states_to_show,
            "show_excluded_items": settings.show_excluded_items,
        }

    @property
    def default_language(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        return portal_state.default_language()

    @property
    def navtree_path(self):
        return get_navigation_root(self.context)

    @property
    def current_language(self):
        return (
            self.request.get("LANGUAGE", None)
            or (self.context and aq_inner(self.context).Language())
            or self.default_language
        )

    @property
    @memoize
    def navtree(self):
        ret = defaultdict(list)
        navtree_path = self.navtree_path
        for tab in self.portal_tabs:
            entry = {}
            entry.update(
                {
                    "path": "/".join((navtree_path, tab["id"])),
                    "description": tab["description"],
                    "@id": tab["url"],
                }
            )
            if "review_state" in tab:
                entry["review_state"] = json_compatible(tab["review_state"])
            else:
                entry["review_state"] = None

            if "title" not in entry:
                entry["title"] = tab.get("name") or tab.get("description") or tab["id"]
            else:
                # translate Home tab
                entry["title"] = translate(
                    entry["title"], domain="plone", context=self.request
                )

            entry["title"] = safe_text(entry["title"])
            ret[navtree_path].append(entry)

        query = {
            "path": {
                "query": self.navtree_path,
                "depth": self.depth,
            },
            "portal_type": {"query": self.settings["displayed_types"]},
            "Language": self.current_language,
            "is_default_page": False,
            "sort_on": "getObjPositionInParent",
        }

        if not self.settings["nonfolderish_tabs"]:
            query["is_folderish"] = True

        if self.settings["filter_on_workflow"]:
            query["review_state"] = list(self.settings["workflow_states_to_show"] or ())

        if not self.settings["show_excluded_items"]:
            query["exclude_from_nav"] = False

        context_path = "/".join(self.context.getPhysicalPath())
        portal_catalog = getToolByName(self.context, "portal_catalog")
        brains = portal_catalog.searchResults(**query)

        registry = getUtility(IRegistry)
        types_using_view = registry.get("plone.types_use_view_action_in_listings", [])

        for brain in brains:
            brain_path = brain.getPath()
            brain_parent_path = brain_path.rpartition("/")[0]
            if brain_parent_path == navtree_path:
                # This should be already provided by the portal_tabs_view
                continue
            if brain.exclude_from_nav and not f"{brain_path}/".startswith(
                f"{context_path}/"
            ):
                # skip excluded items if they're not in our context path
                continue
            url = brain.getURL()
            entry = {
                "path": brain_path,
                "@id": url,
                "title": safe_text(brain.Title),
                "description": safe_text(brain.Description),
                "review_state": json_compatible(brain.review_state),
                "use_view_action_in_listings": brain.portal_type in types_using_view,
            }
            if "nav_title" in brain and brain.nav_title:
                entry.update({"title": brain.nav_title})

            self.customize_entry(entry, brain)
            ret[brain_parent_path].append(entry)
        return ret

    def customize_entry(self, entry, brain):
        """a little helper to add custom entry keys/values."""
        pass

    def render_item(self, item, path):
        sub = self.build_tree(item["path"], first_run=False)

        item.update({"items": sub})

        if "path" in item:
            del item["path"]
        return item

    def build_tree(self, path, first_run=True):
        """Non-template based recursive tree building.
        3-4 times faster than template based.
        """
        out = []
        for item in self.navtree.get(path, []):
            out.append(self.render_item(item, path))

        return out

    @property
    @memoize
    def portal_tabs(self):
        portal_tabs_view = getMultiAdapter(
            (self.context, self.request), name="portal_tabs_view"
        )
        return portal_tabs_view.topLevelTabs()


class NavigationGet(Service):
    def reply(self):
        navigation = Navigation(self.context, self.request)
        return navigation(expand=True)["navigation"]
