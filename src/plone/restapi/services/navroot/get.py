# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


class NavrootGet(Service):
    def reply(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        result = {}
        result["navroot"].update(
            {
                "url": portal_state.navigation_root_url(),
                "title": portal_state.navigation_root_title(),
            }
        )

        return result


class NavrootGet(Service):
    def reply(self):
        navroot = NavrootGet(self.context, self.request)
        return navroot(expand=True)["navroot"]
