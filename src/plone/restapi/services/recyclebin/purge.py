from plone.base.interfaces.recyclebin import IRecycleBin
from plone.restapi.services import Service
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import plone.protect.interfaces


@implementer(IPublishTraverse)
class RecycleBinPurge(Service):
    """DELETE /@recyclebin/{item_id} - Permanently delete an item from the recycle bin
    DELETE /@recyclebin - Empty the entire recycle bin"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@recyclebin as parameters
        self.params.append(name)
        return self

    def reply(self):
        # Disable CSRF protection for this request
        alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

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

        # Handle different cases based on path parameters
        if len(self.params) == 0:
            # DELETE /@recyclebin - Empty the entire recycle bin
            recycle_bin.clear()

            # Return 204 No Content for successful DELETE as per REST conventions
            return self.reply_no_content()
        elif len(self.params) == 1:
            # DELETE /@recyclebin/{item_id} - Delete specific item
            return self._purge_single_item(recycle_bin, self.params[0])
        else:
            self.request.response.setStatus(400)
            return {
                "error": {
                    "type": "BadRequest",
                    "message": "Invalid path parameters",
                }
            }

    def _purge_single_item(self, recycle_bin, item_id):
        """Purge a single item from the recycle bin"""
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

        # Return 204 No Content for successful DELETE as per REST conventions
        return self.reply_no_content()
