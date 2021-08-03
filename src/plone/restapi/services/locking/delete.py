from plone.locking.interfaces import ILockable
from plone.locking.interfaces import INonStealableLock
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.locking import lock_info
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

import plone.protect.interfaces


class Lock(Service):
    """Unlock an object"""

    def reply(self):
        lockable = ILockable(self.context, None)
        if lockable is None:
            return lock_info(self.context)

        data = json_body(self.request)

        # Remove lock by the same user or steal it
        if lockable.can_safely_unlock() or data.get("force"):
            lockable.unlock()

            if INonStealableLock.providedBy(self.context):
                noLongerProvides(self.context, INonStealableLock)

            # Disable CSRF protection
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(
                    self.request, plone.protect.interfaces.IDisableCSRFProtection
                )

        return lock_info(self.context)
