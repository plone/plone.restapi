# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from plone.app.linkintegrity.exceptions import (
    LinkIntegrityNotificationException)
from plone.restapi.services import Service


class ContentDelete(Service):
    """Deletes a content object.
    """

    def reply(self):

        parent = aq_parent(self.context)
        try:
            parent.manage_delObjects([self.context.getId()])
        except LinkIntegrityNotificationException:
            pass

        self.request.response.setStatus(204)
        return None
