from datetime import datetime
from plone.base.interfaces.recyclebin import IRecycleBin
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import boolean_value
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class RecycleBinGet(Service):
    """GET /@recyclebin - List items in the recycle bin
    GET /@recyclebin/{item_id} - Get a specific item from the recycle bin"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@recyclebin as parameters
        self.params.append(name)
        return self

    def reply(self):
        recycle_bin = getUtility(IRecycleBin)

        # Check if recycle bin is enabled
        if not recycle_bin.is_enabled():
            self.request.response.setStatus(404)
            return {
                "error": {
                    "type": "NotFound",
                    "message": "Recycle bin is disabled",
                }
            }

        # If we have a parameter, handle individual item request
        if self.params:
            return self._reply_individual_item(recycle_bin)

        # Otherwise, handle listing request
        return self._reply_listing(recycle_bin)

    def _reply_individual_item(self, recycle_bin):
        """Handle GET /@recyclebin/{item_id} - Get a specific item"""
        if len(self.params) != 1:
            self.request.response.setStatus(400)
            return {
                "error": {
                    "type": "BadRequest",
                    "message": "Invalid URL pattern. Expected: /@recyclebin/{item_id}",
                }
            }

        item_id = self.params[0]

        # Get the specific item from recycle bin
        item = recycle_bin.get_item(item_id)

        if item is None:
            self.request.response.setStatus(404)
            return {
                "error": {
                    "type": "NotFound",
                    "message": f"Item with ID '{item_id}' not found in recycle bin",
                }
            }

        # Convert to serializable format with detailed information
        serialized_item = {
            "@id": f"{self.context.absolute_url()}/@recyclebin/{item_id}",
            "id": item["id"],
            "title": item["title"],
            "@type": item["portal_type"],
            "path": item["path"],
            "parent_path": item["parent_path"],
            "deletion_date": item["deletion_date"].isoformat(),
            "size": item["size"],
            "recycle_id": item_id,
            "deleted_by": item.get("deleted_by", ""),
            "language": item.get("language", ""),
            "review_state": item.get("review_state", ""),
            "has_children": bool(item.get("children")),
            "children_count": len(item.get("children", {})),
            "actions": {
                "restore": f"{self.context.absolute_url()}/@recyclebin/{item_id}/restore",
                "purge": f"{self.context.absolute_url()}/@recyclebin/{item_id}",
            },
        }

        children = []
        for child in item.get("children", {}).values():
            children.append(
                {
                    "id": child["id"],
                    "title": child["title"],
                    "@type": child["portal_type"],
                    "path": child["path"],
                    "size": child["size"],
                }
            )
        serialized_item["children"] = children

        return serialized_item

    def _reply_listing(self, recycle_bin):
        """Handle GET /@recyclebin - List items in the recycle bin"""
        form = self.request.form

        # Parse date parameters
        date_from = date_to = None
        if form.get("date_from"):
            try:
                date_from = datetime.strptime(form["date_from"], "%Y-%m-%d").date()
            except ValueError:
                raise BadRequest("Invalid date_from format. Expected: YYYY-MM-DD")
        if form.get("date_to"):
            try:
                date_to = datetime.strptime(form["date_to"], "%Y-%m-%d").date()
            except ValueError:
                raise BadRequest("Invalid date_to format. Expected: YYYY-MM-DD")

        # Parse has_subitems boolean
        has_subitems_raw = form.get("has_subitems")
        has_subitems = (
            boolean_value(has_subitems_raw) if has_subitems_raw is not None else None
        )

        items = recycle_bin.search(
            title=form.get("title") or None,
            path=form.get("path") or None,
            portal_type=form.get("portal_type") or None,
            date_from=date_from,
            date_to=date_to,
            deleted_by=form.get("deleted_by") or None,
            has_subitems=has_subitems,
            language=form.get("language") or None,
            review_state=form.get("review_state") or None,
            sort_on=form.get("sort_on", "deletion_date"),
            sort_order=form.get("sort_order", "descending"),
        )

        # Convert to serializable format
        serialized_items = [
            {
                "@id": f"{self.context.absolute_url()}/@recyclebin/{item['recycle_id']}",
                "@type": item["portal_type"],
                "id": item["id"],
                "title": item["title"],
                "path": item["path"],
                "parent_path": item["parent_path"],
                "deletion_date": item["deletion_date"].isoformat(),
                "size": item["size"],
                "recycle_id": item["recycle_id"],
                "deleted_by": item.get("deleted_by", ""),
                "language": item.get("language", ""),
                "review_state": item.get("review_state", ""),
                "has_children": bool(item.get("children")),
                "actions": {
                    "restore": f"{self.context.absolute_url()}/@recyclebin/{item['recycle_id']}/restore",
                    "purge": f"{self.context.absolute_url()}/@recyclebin/{item['recycle_id']}",
                },
            }
            for item in items
        ]

        # Apply batching
        batch = HypermediaBatch(self.request, serialized_items)

        results = {}
        results["@id"] = batch.canonical_url
        results["items_total"] = batch.items_total
        links = batch.links
        if links:
            results["batching"] = links

        results["items"] = list(batch)

        return results
