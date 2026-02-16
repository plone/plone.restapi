# TEMPORARY patch for low form memory limit introduced in Zope 5.8.4.
# See https://github.com/plone/Products.CMFPlone/issues/3848
# and https://github.com/zopefoundation/Zope/pull/1180
# Should be removed once `plone.restapi.deserializer.json_body` no longer
# reads the complete request BODY in memory.
from plone.registry.interfaces import IRegistry
from plone.restapi.bbb import INavigationSchema
from Products.CMFPlone.browser.search import Search
from zope.component import getUtility
from ZPublisher.HTTPRequest import ZopeFieldStorage

import logging


logger = logging.getLogger(__name__)
_attr = "VALUE_LIMIT"
_limit = getattr(ZopeFieldStorage, _attr, None)
if _limit:
    setattr(ZopeFieldStorage, _attr, None)
    logger.info(
        "PATCH: Disabled ZPublisher.HTTPRequest.ZopeFieldStorage.%s. "
        "This enables file uploads larger than 1MB.",
        _attr,
    )


# Patch classic Plone search so "Exclude from navigation" is respected (plone/volto#1340).
# Classic UI uses Products.CMFPlone.browser.search.Search, not plone.restapi @search.
def _patch_cmfplone_search_exclude_from_nav():
    try:
        _original_filter_query = Search._filter_query

        def _filter_query_exclude_from_nav(self, query):
            query = _original_filter_query(self, query)
            if query is None:
                return None
            try:
                registry = getUtility(IRegistry)
                nav = registry.forInterface(INavigationSchema, prefix="plone")
                if not nav.show_excluded_items:
                    query["exclude_from_nav"] = False
            except Exception:
                pass
            return query

        Search._filter_query = _filter_query_exclude_from_nav
        logger.info(
            "PATCH: Products.CMFPlone.browser.search.Search now respects "
            "exclude_from_nav (show_excluded_items)."
        )
    except Exception as e:
        logger.debug("Could not patch CMFPlone search for exclude_from_nav: %s", e)


_patch_cmfplone_search_exclude_from_nav()
