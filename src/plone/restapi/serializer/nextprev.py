from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.dexterity.behaviors.nextprevious import NextPreviousBase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class NextPreviousFixed(NextPreviousBase):
    """
    Based on plone.app.dexterity.behaviors.nextprevious.NextPreviousBase
    but works for IPloneSite object
    """

    def __init__(self, context):
        self.context = context
        registry = getUtility(IRegistry)
        self.vat = registry.get('plone.types_use_view_action_in_listings', [])
        self.security = getSecurityManager()
        self.order = self.context.contentIds()


class NextPrevious(object):
    """
    Based on plone.app.dexterity.behaviors.nextprevious.NextPreviousBase
    but works for IPloneSite object
    """

    def __init__(self, context):
        self.context = context
        parent = aq_parent(aq_inner(context))
        self.oldnp = NextPreviousFixed(parent)

    @property
    def next(self):
        """ return info about the next item in the container """
        return self.oldnp.getNextItem(self.context)

    @property
    def previous(self):
        """ return info about the previous item in the container """
        return self.oldnp.getPreviousItem(self.context)
