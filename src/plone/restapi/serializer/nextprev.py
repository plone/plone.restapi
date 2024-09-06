from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.dexterity.behaviors.nextprevious import (
    INextPreviousProvider,
)
from plone.restapi.serializer.utils import get_portal_type_title


class NextPrevious:
    """Facade with more pythonic interface"""

    def __init__(self, context):
        self.context = context
        self.parent = aq_parent(aq_inner(context))
        self.nextprev = INextPreviousProvider(self.parent, None)
        self.enabled = self.nextprev is not None and self.nextprev.enabled

    @property
    def next(self):
        """return info about the next item in the container"""
        if not self.enabled:
            return {}
        if getattr(self.parent, "_ordering", "") == "unordered":
            # Unordered folder
            return {}
        data = self.nextprev.getNextItem(self.context)
        if data is None:
            return {}
        return {
            "@id": data["url"].lstrip("/view"),
            "@type": data["portal_type"],
            "type_title": get_portal_type_title(data.get("portal_type")),
            "title": data["title"],
            "description": data["description"],
        }

    @property
    def previous(self):
        """return info about the previous item in the container"""
        if not self.enabled:
            return {}
        if getattr(self.parent, "_ordering", "") == "unordered":
            # Unordered folder
            return {}
        data = self.nextprev.getPreviousItem(self.context)
        if data is None:
            return {}
        return {
            "@id": data["url"].lstrip("/view"),
            "@type": data["portal_type"],
            "type_title": get_portal_type_title(data.get("portal_type")),
            "title": data["title"],
            "description": data["description"],
        }
