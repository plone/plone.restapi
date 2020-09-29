# -*- coding: utf-8 -*-
from plone.folder.interfaces import IExplicitOrdering
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zExceptions import BadRequest

import six


class OrderingMixin(object):
    def handle_ordering(self, data):
        if "ordering" in data:
            obj_id = data["ordering"]["obj_id"]
            delta = data["ordering"]["delta"]
            subset_ids = data["ordering"].get("subset_ids")

            # The REST api returns only content items and a Zope resource
            # may contain non-content items. We need to set the subset_ids
            # so we'll move items relative to each other.
            if not subset_ids:
                subset_ids = self.context.contentIds()

            self.reorderItems(obj_id, delta, subset_ids)

        if "sort" in data:
            # resort folder items with given parameters
            sort_on = data["sort"]["on"]
            sort_order = data["sort"]["order"]
            self.resortAllItemsInContext(sort_on, sort_order)

    def reorderItems(self, obj_id, delta, subset_ids):
        # Based on wildcard.foldercontents.viewsItemOrder
        ordering = self.getOrdering()
        if ordering is None:
            msg = "Content ordering is not supported by this resource"
            raise BadRequest(msg)

        # Make sure we're seeing the same order as the client is.
        if subset_ids:
            position_id = [(ordering.getObjectPosition(i), i) for i in subset_ids]
            position_id.sort()
            if subset_ids != [i for position, i in position_id]:
                raise BadRequest("Client/server ordering mismatch")

        # Make sure we use bytestring ids for PY2.
        if six.PY2:
            if isinstance(obj_id, six.text_type):
                obj_id = obj_id.encode("utf-8")
            if subset_ids:
                subset_ids = [
                    id_.encode("utf-8") if isinstance(id_, six.text_type) else id_
                    for id_ in subset_ids
                ]

        # All movement is relative to the subset of ids, if passed in.
        if delta == "top":
            ordering.moveObjectsToTop([obj_id], subset_ids=subset_ids)
        elif delta == "bottom":
            ordering.moveObjectsToBottom([obj_id], subset_ids=subset_ids)
        else:
            delta = int(delta)
            ordering.moveObjectsByDelta([obj_id], delta, subset_ids=subset_ids)

    def resortAllItemsInContext(self, sort_on, sort_order):
        # Based on plone.app.content.browser.contents.rearrange
        ordering = self.getOrdering()
        if ordering is None:
            msg = "Content ordering is not supported by this resource"
            raise BadRequest(msg)

        catalog = getToolByName(self.context, "portal_catalog")
        query = {
            "path": {"query": "/".join(self.context.getPhysicalPath()), "depth": 1},
            "sort_on": sort_on,
            "show_inactive": True,
        }
        brains = catalog(**query)
        if sort_order in ("reverse", "descending"):
            brains = [b for b in reversed(brains)]
        for idx, brain in enumerate(brains):
            ordering.moveObjectToPosition(brain.id, idx)

    def getOrdering(self):
        if IPloneSiteRoot.providedBy(self.context):
            return self.context
        elif getattr(self.context, "getOrdering", None):
            ordering = self.context.getOrdering()
            if not IExplicitOrdering.providedBy(ordering):
                return None
            return ordering
