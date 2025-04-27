from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFPlone.interfaces.recyclebin import IRecycleBin
from zExceptions import BadRequest
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import plone.protect.interfaces


@implementer(IPublishTraverse)
class RecycleBinItemDelete(Service):
    """Permanently delete an item from the recyclebin"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.item_id = None

    def publishTraverse(self, request, name):
        self.item_id = name
        return self

    def reply(self):
        if not self.item_id:
            raise BadRequest("No item ID provided")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        recyclebin = getUtility(IRecycleBin)
        success = recyclebin.purge_item(self.item_id)

        if not success:
            self.request.response.setStatus(404)
            return {"error": {"type": "NotFound", "message": "Item not found or cannot be deleted"}}

        return self.reply_no_content()


class RecycleBinEmpty(Service):
    """Empty recyclebin by deleting all items"""

    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        # Check for optional body parameters
        data = {}
        try:
            data = json_body(self.request)
        except Exception:
            pass

        # Optional filter criteria could be added here
        # filter_criteria = data.get("filter", {})

        recyclebin = getUtility(IRecycleBin)
        items = recyclebin.get_items()
        
        purged_count = 0
        failed_items = []
        
        for item in items:
            if recyclebin.purge_item(item["recycle_id"]):
                purged_count += 1
            else:
                failed_items.append(item["recycle_id"])
                
        # If we have failures, return them with a 207 Multi-Status response
        if failed_items:
            self.request.response.setStatus(207)
            return {
                "purged": purged_count,
                "failed": failed_items,
            }
            
        # If everything succeeded, return 204 No Content
        return self.reply_no_content()