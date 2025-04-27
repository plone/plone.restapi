from plone.restapi.services import Service
from Products.CMFPlone.interfaces.recyclebin import IRecycleBin
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
                    "message": "Recycle Bin is disabled",
                }
            }
        
        # Get all items from recycle bin
        items = recycle_bin.get_items()
        
        # Format items for response
        results = []
        for item in items:
            results.append({
                "@id": f"{self.context.absolute_url()}/@recyclebin/{item['recycle_id']}",
                "id": item["id"],
                "title": item["title"],
                "type": item["type"],
                "path": item["path"],
                "parent_path": item["parent_path"],
                "deletion_date": item["deletion_date"].isoformat(),
                "size": item["size"],
                "recycle_id": item["recycle_id"],
                "actions": {
                    "restore": f"{self.context.absolute_url()}/@recyclebin-restore",
                    "purge": f"{self.context.absolute_url()}/@recyclebin-purge"
                }
            })
        
        return {
            "@id": f"{self.context.absolute_url()}/@recyclebin",
            "items": results,
            "items_total": len(results)
        }
