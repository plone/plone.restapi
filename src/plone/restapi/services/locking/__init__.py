"""Locking"""

from datetime import datetime
from datetime import timezone
from plone import api
from plone.locking.interfaces import ILockable


def creator_name(userid):
    user = api.user.get(userid=userid)
    if user:
        return user.getProperty("fullname") or userid
    else:
        return userid


def creator_url(userid):
    url = api.portal.get().absolute_url()
    return f"{url}/author/{userid}"


def creation_date(timestamp):
    # Note that isoformat does not add the Z at the end of the string, The lack of the
    # timezone specifier causes Intl (and derivative libraries) in the browser not to
    # use local time, which is considered a bug in applications. Therefore we add the Z
    # to the end to make sure that the date will be interpreted properly by the client.
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(
        timespec="seconds"
    )


def lock_info(obj):
    """Returns lock information about the given object."""
    lockable = ILockable(obj, None)
    if lockable is not None:
        info = {"locked": lockable.locked(), "stealable": lockable.stealable()}
        lock_info = lockable.lock_info()
        if len(lock_info) > 0:
            creator = lock_info[0]["creator"]
            info["creator"] = creator
            info["creator_name"] = creator_name(creator)
            info["creator_url"] = creator_url(creator)
            created = lock_info[0]["time"]
            info["time"] = created
            info["created"] = creation_date(created)
            info["token"] = lock_info[0]["token"]
            lock_type = lock_info[0]["type"]
            if lock_type:
                info["name"] = lock_info[0]["type"].__name__
            lock_item = webdav_lock(obj)
            if lock_item:
                info["timeout"] = lock_item.getTimeout()
        return info
    return {}


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
