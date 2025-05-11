from plone.base.interfaces.recyclebin import IRecycleBin
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.component import getUtility
from zope.interface import alsoProvides

import plone.protect.interfaces


class RecycleBinRestore(Service):
    """POST /@recyclebin-restore - Restore an item from the recycle bin"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = {}

    def reply(self):
        # Disable CSRF protection for this request
        alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        data = json_body(self.request)
        item_id = data.get("item_id", None)

        if not item_id:
            self.request.response.setStatus(400)
            return {
                "error": {
                    "type": "BadRequest",
                    "message": "Missing required parameter: item_id",
                }
            }

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

        # Get the item to restore
        item_data = recycle_bin.get_item(item_id)
        if not item_data:
            self.request.response.setStatus(404)
            return {
                "error": {
                    "type": "NotFound",
                    "message": f"Item with ID {item_id} not found in recycle bin",
                }
            }

        # Get optional target container path
        target_path = data.get("target_path", None)
        target_container = None

        if target_path:
            try:
                portal = self.context.portal_url.getPortalObject()
                target_container = portal.unrestrictedTraverse(target_path)
            except (KeyError, AttributeError):
                self.request.response.setStatus(400)
                return {
                    "error": {
                        "type": "BadRequest",
                        "message": f"Target path {target_path} not found",
                    }
                }

        # Restore the item
        restored_obj = recycle_bin.restore_item(item_id, target_container)

        if not restored_obj:
            self.request.response.setStatus(500)
            return {
                "error": {
                    "type": "InternalServerError",
                    "message": "Failed to restore item",
                }
            }

        self.request.response.setStatus(200)
        return {
            "status": "success",
            "message": f"Item {item_data['id']} restored successfully",
            "restored_item": {
                "@id": restored_obj.absolute_url(),
                "id": restored_obj.getId(),
                "title": restored_obj.Title(),
                "type": restored_obj.portal_type,
            },
        }
