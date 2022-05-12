from AccessControl import getSecurityManager
from Acquisition import aq_inner
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry
from zExceptions import Unauthorized
from zope.component import queryUtility
from zope.security.interfaces import IPermission


def edit_comment_allowed():
    # Check if editing comments is allowed in the registry
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)
    return settings.edit_comment_enabled


def can_edit(comment):
    """Returns true if current user has the 'Edit comments'
    permission.
    """
    return bool(
        getSecurityManager().checkPermission("Edit comments", aq_inner(comment))
    )


def permission_exists(permission_id):
    permission = queryUtility(IPermission, permission_id)
    return permission is not None


def can_review(comment):
    """Returns true if current user has the 'Review comments' permission."""
    return bool(
        getSecurityManager().checkPermission("Review comments", aq_inner(comment))
    )


def can_delete(comment):
    """Returns true if current user has the 'Delete comments'
    permission.
    """
    if not permission_exists("plone.app.discussion.DeleteComments"):
        # Older versions of p.a.discussion do not support this yet.
        return can_review(comment)

    return bool(
        getSecurityManager().checkPermission("Delete comments", aq_inner(comment))
    )


def delete_own_comment_allowed():
    if not permission_exists("plone.app.discussion.DeleteOwnComments"):
        # Older versions of p.a.discussion do not support this yet.
        return False
    # Check if delete own comments is allowed in the registry
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)
    return settings.delete_own_comment_enabled


def can_delete_own(comment):
    """Returns true if the current user could delete the comment if it had
    no replies. This is used to prepare hidden form buttons for JS.
    """
    if not permission_exists("plone.app.discussion.DeleteOwnComments"):
        # Older versions of p.a.discussion do not support this yet.
        return False
    try:
        return comment.restrictedTraverse("@@delete-own-comment").could_delete()
    except Unauthorized:
        return False
