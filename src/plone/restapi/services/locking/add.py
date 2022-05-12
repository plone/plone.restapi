from plone.locking.interfaces import INonStealableLock
from plone.locking.interfaces import IRefreshableLockable
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.locking import lock_info
from plone.restapi.services.locking import webdav_lock
from zope.interface import alsoProvides

import plone.protect.interfaces


class Lock(Service):
    """Lock an object"""

    def reply(self):
        data = json_body(self.request)

        lockable = IRefreshableLockable(self.context, None)
        if lockable is not None:
            lockable.lock()

            if "stealable" in data and not data["stealable"]:
                alsoProvides(self.context, INonStealableLock)

            if "timeout" in data:
                lock_item = webdav_lock(self.context)
                lock_item.setTimeout("Second-%s" % data["timeout"])

            # Disable CSRF protection
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(
                    self.request, plone.protect.interfaces.IDisableCSRFProtection
                )

        return lock_info(self.context)
