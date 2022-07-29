# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from zope.component import getMultiAdapter


class SiteGet(Service):
    def reply(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        return {
            "title": portal_state.portal_title(),
        }
