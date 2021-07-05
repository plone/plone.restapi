from plone.locking.interfaces import ILockable
from plone.locking.interfaces import INonStealableLock
from plone.locking.interfaces import IRefreshableLockable
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

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


class Unlock(Service):
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


class RefreshLock(Service):
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


class LockInfo(Service):
    """Lock information about the current lock"""

    def reply(self):
        return lock_info(self.context)


def lock_info(obj):
    """Returns lock information about the given object."""
    lockable = ILockable(obj, None)
    if lockable is not None:
        info = {"locked": lockable.locked(), "stealable": lockable.stealable()}
        lock_info = lockable.lock_info()
        if len(lock_info) > 0:
            info["creator"] = lock_info[0]["creator"]
            info["time"] = lock_info[0]["time"]
            info["token"] = lock_info[0]["token"]
            lock_type = lock_info[0]["type"]
            if lock_type:
                info["name"] = lock_info[0]["type"].__name__
            lock_item = webdav_lock(obj)
            if lock_item:
                info["timeout"] = lock_item.getTimeout()
        return info


def webdav_lock(obj):
    """Returns the WebDAV LockItem"""
    lockable = ILockable(obj, None)
    if lockable is None:
        return

    lock_info = lockable.lock_info()
    if len(lock_info) > 0:
        token = lock_info[0]["token"]
        return obj.wl_getLock(token)


def is_locked(obj, request):
    """Returns true if the object is locked and the request doesn't contain
    the lock token.
    """
    lockable = ILockable(obj, None)
    if lockable is None:
        return False
    if lockable.locked():
        token = request.getHeader("Lock-Token", "")
        lock_info = lockable.lock_info()
        if len(lock_info) > 0 and lock_info[0]["token"] == token:
            return False
        return True
    return False
