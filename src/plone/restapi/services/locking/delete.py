from plone.locking.interfaces import ILockable
from plone.locking.interfaces import INonStealableLock
from plone.restapi.services import Service
from plone.restapi.services.locking import lock_info
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

import plone.protect.interfaces


class Lock(Service):
    """Unlock an object"""

    def reply(self):
        lockable = ILockable(self.context)
        if lockable.can_safely_unlock():
            lockable.unlock()

            if INonStealableLock.providedBy(self.context):
                noLongerProvides(self.context, INonStealableLock)

            # Disable CSRF protection
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(
                    self.request, plone.protect.interfaces.IDisableCSRFProtection
                )

        return lock_info(self.context)
