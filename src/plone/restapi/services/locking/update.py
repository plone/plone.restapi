from plone.locking.interfaces import IRefreshableLockable
from plone.restapi.services import Service
from plone.restapi.services.locking import lock_info
from zope.interface import alsoProvides

import plone.protect.interfaces


class Lock(Service):
    """Refresh the lock of an object"""

    def reply(self):
        lockable = IRefreshableLockable(self.context, None)
        if lockable is not None:
            lockable.refresh_lock()

            # Disable CSRF protection
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(
                    self.request, plone.protect.interfaces.IDisableCSRFProtection
                )

        return lock_info(self.context)
