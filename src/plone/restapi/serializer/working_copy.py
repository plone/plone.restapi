"""
$Id: base.py 1808 2007-02-06 11:39:11Z hazmat $
"""

from AccessControl import getSecurityManager
from DateTime import DateTime
from plone.app.iterate.interfaces import IBaseline
from plone.app.iterate.interfaces import ICheckinCheckoutPolicy
from plone.app.iterate.interfaces import keys
from plone.app.iterate.permissions import CheckoutPermission
from plone.memoize.instance import memoize
from plone.restapi.serializer.converters import json_compatible
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.log import logger
from Products.Five.browser import BrowserView


class WorkingCopyInfo(BrowserView):
    def __init__(self, context):
        self.context = context
        self.ref = None

    def get_working_copy_info(self):
        baseline = self.baseline()
        working_copy = self.working_copy()

        sm = getSecurityManager()

        # No Working Copy exists
        if baseline is None and working_copy is None:
            return (None, None)

        # Baseline is None (context is the baseline), and working copy exists
        if baseline is None and working_copy:
            self.ref = working_copy

            if (
                sm.checkPermission(ModifyPortalContent, self.context)
                or sm.checkPermission(CheckoutPermission, self.context)
                or sm.checkPermission(ModifyPortalContent, working_copy)
            ):
                return (
                    None,
                    {
                        "@id": working_copy.absolute_url(),
                        "title": working_copy.title,
                        "created": json_compatible(self.created()),
                        "creator_url": self.creator_url(),
                        "creator_name": self.creator_name(),
                    },
                )
            else:
                return (None, None)

        # Baseline exist (context is the working copy), and working copy exists
        if baseline and working_copy:
            self.ref = baseline

            if sm.checkPermission(
                ModifyPortalContent, self.context
            ) or sm.checkPermission(CheckoutPermission, baseline):
                return (
                    {"@id": baseline.absolute_url(), "title": baseline.title},
                    {
                        "@id": working_copy.absolute_url(),
                        "title": working_copy.title,
                        "created": json_compatible(self.created()),
                        "creator_url": self.creator_url(),
                        "creator_name": self.creator_name(),
                    },
                )
            else:
                return (None, None)

    @property
    @memoize
    def policy(self):
        return ICheckinCheckoutPolicy(self.context)

    @memoize
    def working_copy(self):
        return self.policy.getWorkingCopy()

    @memoize
    def baseline(self):
        return self.policy.getBaseline()

    @memoize
    def created(self):
        return self.properties.get(keys.checkout_time, DateTime())

    @memoize
    def creator(self):
        user_id = self.properties.get(keys.checkout_user)
        membership = getToolByName(self.context, "portal_membership")
        if not user_id:
            return membership.getAuthenticatedMember()
        return membership.getMemberById(user_id)

    @memoize
    def creator_url(self):
        creator = self.creator()
        if creator is not None:
            portal_url = getToolByName(self.context, "portal_url")
            return f"{portal_url()}/author/{creator.getId()}"

    @memoize
    def creator_name(self):
        creator = self.creator()
        if creator is not None:
            return creator.getProperty("fullname") or creator.getId()
        # User is not known by PAS. This may be due to LDAP issues, so we keep
        # the user and log this.
        name = self.properties.get(keys.checkout_user)
        if IBaseline.providedBy(self.context):
            warning_tpl = (
                "%s is a baseline of a plone.app.iterate checkout "
                'by an unknown user id "%s"'
            )
        else:
            # IWorkingCopy.providedBy(self.context)
            warning_tpl = (
                "%s is a working copy of a plone.app.iterate "
                'checkout by an unknown user id "%s"'
            )
        logger.warning(warning_tpl, self.context, name)
        return name

    @property
    @memoize
    def properties(self):
        if self.ref:
            return self.policy.getProperties(self.ref, default={})
        else:
            return {}
