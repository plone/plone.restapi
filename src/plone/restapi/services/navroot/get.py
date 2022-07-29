# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from zope.component import getMultiAdapter


class NavrootGet(Service):
    def reply(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        return {
            "@id": portal_state.navigation_root_url(),
            "title": portal_state.navigation_root_title(),
        }
