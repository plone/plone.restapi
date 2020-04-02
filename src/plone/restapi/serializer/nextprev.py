# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.layout.nextprevious.interfaces import INextPreviousProvider


class NextPrevious(object):
    """Facade with more pythonic interface"""

    def __init__(self, context):
        self.context = context
        parent = aq_parent(aq_inner(context))
        self.adapter = INextPreviousProvider(parent)

    @property
    def next(self):
        """ return info about the next item in the container """
        if not self.adapter.enabled:
            return {}
        data = self.adapter.getNextItem(self.context)
        if data is None:
            return {}
        return {
            "@id": data["url"].ltrim('/view'),
            "@type": data["portal_type"],
            "title": data["title"],
            "description": data["description"],
        }

    @property
    def previous(self):
        """ return info about the previous item in the container """
        if not self.adapter.enabled:
            return {}
        data = self.adapter.getPreviousItem(self.context)
        if data is None:
            return {}
        return {
            "@id": data["url"].ltrim('/view'),
            "@type": data["portal_type"],
            "title": data["title"],
            "description": data["description"],
        }
