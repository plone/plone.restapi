from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.users import UnrestrictedUser as BaseUnrestrictedUser
from contextlib import contextmanager
from zope.component import getMultiAdapter


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id."""

    def getId(self):
        """Return the ID of the user."""
        return self.getUserName()


@contextmanager
def elevated_privileges(context):
    """Temporarily elevate current user's privileges.

    See http://docs.plone.org/develop/plone/security/permissions.html
    for more documentation on this code.

    """
    sm = getSecurityManager()
    try:
        portal = getMultiAdapter(
            (context, context.REQUEST), name="plone_portal_state"
        ).portal()
        tmp_user = UnrestrictedUser(sm.getUser().getId(), "", ("manage", "Manager"), "")
        tmp_user = tmp_user.__of__(portal.acl_users)
        newSecurityManager(None, tmp_user)

        yield
    finally:
        setSecurityManager(sm)
