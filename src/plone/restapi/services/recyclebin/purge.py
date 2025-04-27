from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFPlone.interfaces.recyclebin import IRecycleBin
from zope.component import getUtility
from zope.interface import alsoProvides

import plone.protect.interfaces


class RecycleBinPurge(Service):
    """POST /@recyclebin-purge - Permanently delete an item from the recycle bin"""
    
    def reply(self):
        # Disable CSRF protection for this request
        alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
        
        data = json_body(self.request)
        item_id = data.get("item_id", None)
        purge_all = data.get("purge_all", False)
        purge_expired = data.get("purge_expired", False)
        
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
        
        # Handle purging all items
        if purge_all:
            purged_count = 0
            for item in recycle_bin.get_items():
                if recycle_bin.purge_item(item["recycle_id"]):
                    purged_count += 1
            
            return {
                "status": "success",
                "purged_count": purged_count,
                "message": f"Purged {purged_count} items from recycle bin"
            }
        
        # Handle purging expired items
        if purge_expired:
            purged_count = recycle_bin.purge_expired_items()
            
            return {
                "status": "success",
                "purged_count": purged_count,
                "message": f"Purged {purged_count} expired items from recycle bin"
            }
        
        # Handle purging a specific item
        if not item_id:
            self.request.response.setStatus(400)
            return {
                "error": {
                    "type": "BadRequest",
                    "message": "Missing required parameter: item_id or purge_all or purge_expired",
                }
            }
        
        # Get the item to purge
        item_data = recycle_bin.get_item(item_id)
        if not item_data:
            self.request.response.setStatus(404)
            return {
                "error": {
                    "type": "NotFound",
                    "message": f"Item with ID {item_id} not found in recycle bin",
                }
            }
        
        # Purge the item
        success = recycle_bin.purge_item(item_id)
        
        if not success:
            self.request.response.setStatus(500)
            return {
                "error": {
                    "type": "InternalServerError",
                    "message": "Failed to purge item",
                }
            }
        
        return {
            "status": "success",
            "message": f"Item {item_data['id']} purged successfully"
        }
