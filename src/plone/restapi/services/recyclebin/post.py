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
class RecycleBinItemRestore(Service):
    """Restore an item from the recyclebin"""

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
        restored = recyclebin.restore_item(self.item_id)

        if not restored:
            self.request.response.setStatus(404)
            return {"error": {"type": "NotFound", "message": "Item not found or cannot be restored"}}

        self.request.response.setStatus(200)
        return {
            "status": "success",
            "message": "Item restored successfully",
            "@id": restored.absolute_url(),
            "title": getattr(restored, "title", ""),
            "path": "/".join(restored.getPhysicalPath())
        }