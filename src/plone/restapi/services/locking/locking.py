# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from plone.locking.interfaces import ILockable
from plone.locking.interfaces import IRefreshableLockable


class Lock(Service):
    """Lock an object"""

    def reply(self):
        lockable = IRefreshableLockable(self.context, None)
        if lockable is not None:
            lockable.lock()
        return lock_info(self.context)


class Unlock(Service):
    """Unlock an object"""

    def reply(self):
        lockable = ILockable(self.context)
        if lockable.can_safely_unlock():
            lockable.unlock()
        return lock_info(self.context)


class RefreshLock(Service):
    """Refresh the lock of an object"""

    def reply(self):
        lockable = IRefreshableLockable(self.context, None)
        if lockable is not None:
            lockable.refresh_lock()
        return lock_info(self.context)


class LockInfo(Service):
    """Lock inforation of an object"""

    def reply(self):
        return lock_info(self.context)


def lock_info(obj):
    """Returns lock information about the given object."""
    lockable = ILockable(obj)
    if lockable is not None:
        info = {
            'locked': lockable.locked(),
            'stealable': lockable.stealable(),
        }
        lock_info = lockable.lock_info()
        if len(lock_info) > 0:
            info['creator'] = lock_info[0]['creator']
            info['time'] = lock_info[0]['time']
            info['token'] = lock_info[0]['token']
            info['timeout'] = lock_info[0]['type'].timeout
        return info
