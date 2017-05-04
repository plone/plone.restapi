# -*- coding: utf-8 -*-
from plone.restapi.controlpanels import IControlpanel
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.services import Service
from zope.component import getAdapters
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zExceptions import BadRequest


@implementer(IPublishTraverse)
class ControlpanelsPatch(Service):
    controlpanel_name = None

    def publishTraverse(self, request, name):
        self.controlpanel_name = name
        return self

    def get_controlpanel_adapters(self):
        adapters = getAdapters(
            (self.context, self.request),
            provided=IControlpanel
        )
        for name, panel in adapters:
            panel.__name__ = name
            yield name, panel

    def panel_by_name(self, name):
        panels = dict(self.get_controlpanel_adapters())
        return panels.get(name)

    def reply(self):
        if not self.controlpanel_name:
            raise BadRequest('Missing parameter controlpanelname')

        panel = self.panel_by_name(self.controlpanel_name)
        deserializer = IDeserializeFromJson(panel)
        deserializer()  # The deserializer knows where to put it.

        self.request.response.setStatus(204)
