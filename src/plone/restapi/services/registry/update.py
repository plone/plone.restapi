# -*- coding: utf-8 -*-
from plone.rest import Service


class RegistryUpdate(Service):

    def render(self):
        self.request.response.setStatus(204)
        return None
