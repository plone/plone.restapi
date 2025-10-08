from datetime import datetime
from plone.base.interfaces.recyclebin import IRecycleBin
from plone.restapi.batching import HypermediaBatch
from plone.restapi.services import Service
from zope.component import getUtility


class RecycleBinGet(Service):
    """GET /@recyclebin - List items in the recycle bin"""

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

        # Get all items from recycle bin
        all_items = recycle_bin.get_items()

        # Apply filters
        filtered_items = self._apply_filters(all_items)

        # Apply sorting
        sorted_items = self._apply_sorting(filtered_items)

        # Convert to serializable format
        serialized_items = []
        for item in sorted_items:
            serialized_items.append(
                {
                    "@id": f"{self.context.absolute_url()}/@recyclebin/{item['recycle_id']}",
                    "id": item["id"],
                    "title": item["title"],
                    "type": item["type"],
                    "path": item["path"],
                    "parent_path": item["parent_path"],
                    "deletion_date": item["deletion_date"].isoformat(),
                    "size": item["size"],
                    "recycle_id": item["recycle_id"],
                    "deleted_by": item.get("deleted_by", ""),
                    "language": item.get("language", ""),
                    "workflow_state": item.get("workflow_state", ""),
                    "has_children": "children" in item and len(item["children"]) > 0,
                    "actions": {
                        "restore": f"{self.context.absolute_url()}/@recyclebin/{item['recycle_id']}/restore",
                        "purge": f"{self.context.absolute_url()}/@recyclebin/{item['recycle_id']}",
                    },
                }
            )

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

    def _apply_filters(self, items):
        """Apply filters based on request parameters"""
        form = self.request.form

        # Get filter parameters
        search_query = form.get("search_query", "").lower()
        filter_type = form.get("filter_type", "")
        date_from_str = form.get("date_from", "")
        date_to_str = form.get("date_to", "")
        filter_deleted_by = form.get("filter_deleted_by", "")
        filter_has_subitems = form.get("filter_has_subitems", "")
        filter_language = form.get("filter_language", "")
        filter_workflow_state = form.get("filter_workflow_state", "")

        # Parse dates
        date_from = None
        date_to = None
        try:
            if date_from_str:
                date_from = datetime.strptime(date_from_str, "%Y-%m-%d").date()
            if date_to_str:
                date_to = datetime.strptime(date_to_str, "%Y-%m-%d").date()
        except ValueError:
            # Invalid date format, ignore
            pass

        filtered_items = []

        for item in items:
            # Apply content type filtering
            if filter_type and item.get("type") != filter_type:
                continue

            # Apply date range filtering
            if date_from or date_to:
                deletion_date = item.get("deletion_date")
                if deletion_date:
                    item_date = (
                        deletion_date.date()
                        if hasattr(deletion_date, "date")
                        else deletion_date
                    )
                    if date_from and item_date < date_from:
                        continue
                    if date_to and item_date > date_to:
                        continue

            # Apply deleted by filtering
            if filter_deleted_by and item.get("deleted_by") != filter_deleted_by:
                continue

            # Apply has subitems filtering
            if filter_has_subitems:
                has_children = "children" in item and len(item["children"]) > 0
                if filter_has_subitems == "with_subitems" and not has_children:
                    continue
                elif filter_has_subitems == "without_subitems" and has_children:
                    continue

            # Apply language filtering
            if filter_language and item.get("language") != filter_language:
                continue

            # Apply workflow state filtering
            if (
                filter_workflow_state
                and item.get("workflow_state") != filter_workflow_state
            ):
                continue

            # Apply search query filtering
            if search_query:
                title = item.get("title", "").lower()
                path = item.get("path", "").lower()
                if search_query not in title and search_query not in path:
                    continue

            filtered_items.append(item)

        return filtered_items

    def _apply_sorting(self, items):
        """Apply sorting based on request parameters"""
        sort_by = self.request.form.get("sort_by", "date_desc")

        if sort_by == "title_asc":
            items.sort(key=lambda x: x.get("title", "").lower())
        elif sort_by == "title_desc":
            items.sort(key=lambda x: x.get("title", "").lower(), reverse=True)
        elif sort_by == "type_asc":
            items.sort(key=lambda x: x.get("type", "").lower())
        elif sort_by == "type_desc":
            items.sort(key=lambda x: x.get("type", "").lower(), reverse=True)
        elif sort_by == "path_asc":
            items.sort(key=lambda x: x.get("path", "").lower())
        elif sort_by == "path_desc":
            items.sort(key=lambda x: x.get("path", "").lower(), reverse=True)
        elif sort_by == "size_asc":
            items.sort(key=lambda x: x.get("size", 0))
        elif sort_by == "size_desc":
            items.sort(key=lambda x: x.get("size", 0), reverse=True)
        elif sort_by == "date_asc":
            items.sort(key=lambda x: x.get("deletion_date", datetime.now()))
        elif sort_by == "workflow_asc":
            items.sort(key=lambda x: (x.get("workflow_state") or "").lower())
        elif sort_by == "workflow_desc":
            items.sort(
                key=lambda x: (x.get("workflow_state") or "").lower(), reverse=True
            )
        else:
            # Default: date_desc
            items.sort(
                key=lambda x: x.get("deletion_date", datetime.now()), reverse=True
            )

        return items
