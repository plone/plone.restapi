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
        self.request.response.setStatus(204)
        return super(Lock, self).reply()


class Unlock(Service):
    """Unlock an object"""

    def reply(self):
        lockable = ILockable(self.context)
        if lockable.can_safely_unlock():
            lockable.unlock()
        self.request.response.setStatus(204)
        return super(Unlock, self).reply()


class RefreshLock(Service):
    """Refresh the lock of an object"""

    def reply(self):
        lockable = IRefreshableLockable(self.context, None)
        if lockable is not None:
            lockable.refresh_lock()
        self.request.response.setStatus(204)
        return super(RefreshLock, self).reply()


class LockInfo(Service):
    """Returns lock information about an object"""

    def reply(self):
        lockable = ILockable(self.context)
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
