from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from Products.CMFPlone.interfaces.recyclebin import IRecycleBin
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class RecycleBin:
    """Get recyclebin information."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {"recyclebin": {"@id": f"{self.context.absolute_url()}/@recyclebin"}}
        if not expand:
            return result

        recyclebin = getUtility(IRecycleBin)
        items = recyclebin.get_items()
        
        results = []
        for item in items:
            # Exclude the actual object from the response
            data = {k: v for k, v in item.items() if k != "object"}
            # Convert datetime to ISO format
            if "deletion_date" in data:
                data["deletion_date"] = data["deletion_date"].isoformat()
            results.append(data)
            
        return {"recyclebin": {"items": results, "items_total": len(results)}}


class RecycleBinGet(Service):
    """Get list of all items in recyclebin"""

    def reply(self):
        recyclebin = RecycleBin(self.context, self.request)
        return recyclebin(expand=True)["recyclebin"]


@implementer(IPublishTraverse)
class RecycleBinItemGet(Service):
    """Get a specific item from the recyclebin"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.item_id = None

    def publishTraverse(self, request, name):
        self.item_id = name
        return self

    def reply(self):
        if not self.item_id:
            return self.reply_no_content(status=404)
            
        recyclebin = getUtility(IRecycleBin)
        item = recyclebin.get_item(self.item_id)
        
        if not item:
            return self.reply_no_content(status=404)
            
        # Exclude the actual object from the response
        data = {k: v for k, v in item.items() if k != "object"}
        # Convert datetime to ISO format
        if "deletion_date" in data:
            data["deletion_date"] = data["deletion_date"].isoformat()
            
        return data