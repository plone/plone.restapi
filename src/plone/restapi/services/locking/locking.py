import warnings
from zope.deprecation import deprecated
from plone.restapi.services.locking import lock_info
from plone.restapi.services.locking import webdav_lock
from plone.restapi.services.locking import is_locked

from plone.restapi.services.locking.add import Lock as AddLock
from plone.restapi.services.locking.get import Lock as GetLock
from plone.restapi.services.locking.delete import Lock as DeleteLock
from plone.restapi.services.locking.update import Lock as UpdateLock


lock_info = deprecated(
    lock_info,
    "``plone.restapi.services.locking.locking.lock_info`` is deprecated and will be removed in plone.restapi 9.0. Use it from ``plone.restapi.services.locking`` instead.",
)
webdav_lock = deprecated(
    webdav_lock,
    "``plone.restapi.services.locking.locking.webdav_lock`` is deprecated and will be removed in plone.restapi 9.0. Use it from ``plone.restapi.services.locking`` instead.",
)
is_locked = deprecated(
    is_locked,
    "``plone.restapi.services.locking.locking.is_locked`` is deprecated and will be removed in plone.restapi 9.0. Use it from ``plone.restapi.services.locking`` instead.",
)


class Lock(AddLock):
    """Lock an object"""

    def reply(self):
        warnings.warn(
            "``plone.restapi.services.locking.Lock`` is deprecated and will be removed in plone.restapi 9.0. Use it from ``plone.restapi.services.locking.update`` instead.",
            DeprecationWarning,
        )
        return super(Lock, self).reply()


class Unlock(DeleteLock):
    """Unlock an object"""

    def reply(self):
        warnings.warn(
            "``POST @unlock`` endpoint is deprecated and will be removed in plone.restapi 9.0. Use ``DELETE @lock`` instead.",
            DeprecationWarning,
        )
        return super(Unlock, self).reply()


class RefreshLock(UpdateLock):
    """Refresh the lock of an object"""

    def reply(self):
        warnings.warn(
            "``POST @refresh-lock`` endpoint is deprecated and will be removed in plone.restapi 9.0. Use ``PATCH @lock`` instead.",
            DeprecationWarning,
        )
        return super(RefreshLock, self).reply()


class LockInfo(GetLock):
    """Lock information about the current lock"""

    def reply(self):
        warnings.warn(
            "``plone.restapi.services.locking.LockInfo`` is deprecated and will be removed in plone.restapi 9.0. Use it from ``plone.restapi.services.locking.get`` instead.",
            DeprecationWarning,
        )
        return super(LockInfo, self).reply()
