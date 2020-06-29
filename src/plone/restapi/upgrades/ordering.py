# -*- coding: utf-8 -*-
from persistent.list import PersistentList
from plone.folder.default import DefaultOrdering
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations

import six


ORDER_KEY = DefaultOrdering.ORDER_KEY
QUERY = {"is_folderish": True}


def safe_utf8(to_utf8):
    if isinstance(to_utf8, six.text_type):
        to_utf8 = to_utf8.encode("utf-8")
    return to_utf8


def ensure_child_ordering_object_ids_are_native_strings(container):
    """Make sure the ordering stored on parent contains only native_string
    object ids.

    This function can be used to fix ordering object ids stored on a parent
    object in a `DefaultOrdering` ordering adapter. When changing object
    ordering via PATCH request we used to incorrectly store ids of reordered
    resouces as unicode instead of a bytestring (on python 2). This
    lead to mixed types being stored in the ordering annotations and
    subsequently mixed types being returned when calling `objectIds` of a
    container.

    The problem only exists with python 2 so we do nothing when we are
    called on python 3 by mistake.
    """
    if six.PY3:
        return

    if not IAnnotatable.providedBy(container):
        return

    annotations = IAnnotations(container)
    if ORDER_KEY not in annotations:
        return

    fixed_ordering = PersistentList(
        safe_utf8(item_id) for item_id in annotations[ORDER_KEY]
    )
    annotations[ORDER_KEY] = fixed_ordering


class FixOrderingView(BrowserView):
    """Attempt to fix ordering for all potentially affected objects.

    By default will fix ordering object ids for every object that considers
    itself folderish.

    The problem only exists with python 2 so we do nothing when we are
    called on python 3 by mistake.
    """

    def __call__(self):
        if six.PY3:
            return "Aborted, fixing ordering is only necessary on python 2."

        catalog = getToolByName(self.context, "portal_catalog")
        for brain in catalog.unrestrictedSearchResults(QUERY):
            folderish = brain.getObject()
            ensure_child_ordering_object_ids_are_native_strings(folderish)

        return "Done."
