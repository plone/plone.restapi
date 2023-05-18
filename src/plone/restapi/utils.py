from AccessControl import ClassSecurityInfo
from operator import itemgetter
from plone.app.querystring import queryparser
from plone.app.querystring.interfaces import IParsedQueryIndexModifier
from AccessControl.Permissions import search_zcatalog as SearchZCatalog
from zope.component import getUtilitiesFor, getUtility
from AccessControl.SecurityManagement import getSecurityManager
from plone.app.querystring.interfaces import IQueryModifier
from Products.CMFCore.indexing import processQueue
from Products.CMFCore.interfaces import ICatalogTool
from DateTime import DateTime


import logging
import re

logger = logging.getLogger("plone.app.querystring")

# We should accept both a simple space, unicode u'\u0020 but also a
# multi-space, so called 'waji-kankaku', unicode u'\u3000'
_MULTISPACE = "\u3000"
_BAD_CHARS = ("?", "-", "+", "*", _MULTISPACE)

security = ClassSecurityInfo()

def _quote_chars(s):
    # We need to quote parentheses when searching text indices
    if "(" in s:
        s = s.replace("(", '"("')
    if ")" in s:
        s = s.replace(")", '")"')
    if _MULTISPACE in s:
        s = s.replace(_MULTISPACE, " ")
    return s

def _quote(term):
    # The terms and, or and not must be wrapped in quotes to avoid
    # being parsed as logical query atoms.
    if term.lower() in ("and", "or", "not"):
        term = '"%s"' % term
    return term


def munge_search_term(query):
    for char in _BAD_CHARS:
        query = query.replace(char, " ")

    # extract quoted phrases first
    quoted_phrases = re.findall(r'"([^"]*)"', query)
    r = []
    for qp in quoted_phrases:
        # remove from original query
        query = query.replace(f'"{qp}"', "")
        # replace with cleaned leading/trailing whitespaces
        # and skip empty phrases
        clean_qp = qp.strip()
        if not clean_qp:
            continue
        r.append(f'"{clean_qp}"')

    r += map(_quote, query.strip().split())
    r = " AND ".join(r)
    r = _quote_chars(r) + ("*" if r and not r.endswith('"') else "")
    return r


def filter_query(query):
    text = query.get("SearchableText", None)
    if isinstance(text, dict):
        text = text.get("query", "")
    if text:
        query["SearchableText"] = munge_search_term(text)
    return query

def get_query(
    context,
    query=None,
    batch=False,
    b_start=0,
    b_size=30,
    sort_on=None,
    sort_order=None,
    limit=0,
    custom_query=None,
    **kw
):
    """Parse the (form)query and return using multi-adapter"""
    query_modifiers = getUtilitiesFor(IQueryModifier)
    for name, modifier in sorted(query_modifiers, key=itemgetter(0)):
        query = modifier(query)

    parsedquery = queryparser.parseFormquery(
        context, query, sort_on, sort_order
    )

    index_modifiers = getUtilitiesFor(IParsedQueryIndexModifier)
    for name, modifier in index_modifiers:
        if name in parsedquery:
            new_name, query = modifier(parsedquery[name])
            parsedquery[name] = query
            # if a new index name has been returned, we need to replace
            # the native ones
            if name != new_name:
                del parsedquery[name]
                parsedquery[new_name] = query

    # Check for valid indexes
    ctool = getUtility(ICatalogTool)
    valid_indexes = [index for index in parsedquery if index in ctool.indexes()]

    # We'll ignore any invalid index, but will return an empty set if none
    # of the indexes are valid.
    if not valid_indexes:
        logger.warning("Using empty query because there are no valid indexes used.")
        parsedquery = {}

    if batch:
        parsedquery["b_start"] = b_start
        parsedquery["b_size"] = b_size
    elif limit:
        parsedquery["sort_limit"] = limit

    if "path" not in parsedquery:
        parsedquery["path"] = {"query": ""}

    if isinstance(custom_query, dict) and custom_query:
        # Update the parsed query with an extra query dictionary. This may
        # override the parsed query. The custom_query is a dictionary of
        # index names and their associated query values.
        for key in custom_query:
            if isinstance(parsedquery.get(key), dict) and isinstance(
                custom_query.get(key), dict
            ):
                parsedquery[key].update(custom_query[key])
                continue
            parsedquery[key] = custom_query[key]

    # filter bad term and operator in query
    parsedquery = filter_query(parsedquery)
    return parsedquery

@security.protected(SearchZCatalog)
def searchResults(query=None, **kw):
    # =================== CatalogTool
    # Calls ZCatalog.searchResults with extra arguments that
    # limit the results to what the user is allowed to see.
    #
    # This version uses the 'effectiveRange' DateRangeIndex.
    #
    # It also accepts a keyword argument show_inactive to disable
    # effectiveRange checking entirely even for those without portal
    # wide AccessInactivePortalContent permission.

    # Make sure any pending index tasks have been processed
    processQueue()

    ctool = getUtility(ICatalogTool)

    kw = kw.copy()
    show_inactive = kw.get('show_inactive', False)
    if isinstance(query, dict) and not show_inactive:
        show_inactive = 'show_inactive' in query

    user = getSecurityManager().getUser()
    kw['allowedRolesAndUsers'] = ctool._listAllowedRolesAndUsers(user)

    if not show_inactive and not ctool.allow_inactive(kw):
        kw['effectiveRange'] = DateTime()

    # filter out invalid sort_on indexes
    sort_on = kw.get('sort_on') or []
    if isinstance(sort_on, str):
        sort_on = [sort_on]
    valid_indexes = ctool.indexes()
    try:
        sort_on = [idx for idx in sort_on if idx in valid_indexes]
    except TypeError:
        # sort_on is not iterable
        sort_on = []
    if not sort_on:
        kw.pop('sort_on', None)
    else:
        kw['sort_on'] = sort_on
    # ==================== Catalog searchresults
    # You should pass in a simple dictionary as the first argument,
    # which only contains the relevant query.
    query = ctool._catalog.merge_query_args(query, **kw)
    sort_indexes = ctool._catalog._getSortIndex(query)
    reverse = False
    if sort_indexes is not None:
        order = ctool._catalog._get_sort_attr("order", query)
        reverse = []
        if order is None:
            order = ['']
        elif isinstance(order, str):
            order = [order]
        for o in order:
            reverse.append(o.lower() in ('reverse', 'descending'))
        if len(reverse) == 1:
            # be nice and keep the old API intact for single sort_order
            reverse = reverse[0]
    # ===================== Catalog search
    # Indexes fulfill a fairly large contract here. We hand each
    # index the query mapping we are given (which may be composed
    # of some combination of web request, kw mappings or plain old dicts)
    # and the index decides what to do with it. If the index finds work
    # for itself in the query, it returns the results and a tuple of
    # the attributes that were used. If the index finds nothing for it
    # to do then it returns None.

    # Canonicalize the request into a sensible query before passing it on
    query = ctool._catalog.make_query(query)

    cr = ctool._catalog.getCatalogPlan(query)
    cr.start()

    plan = cr.plan()
    if not plan:
        plan = ctool._catalog._sorted_search_indexes(query)

    rs = None  # result set
    for index_id in plan:
        # The actual core loop over all indices.
        if index_id not in ctool._catalog.indexes:
            # We can have bogus keys or the plan can contain index names
            # that have been removed in the meantime.
            continue

        rs = ctool._catalog._search_index(cr, index_id, query, rs)
        if not rs:
            break
    return rs