# -*- coding: utf-8 -*-
from plone.restapi.controlpanels import IControlpanel
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getAdapters
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class ControlpanelsAdd(Service):
    def __init__(self, context, request):
        super(ControlpanelsAdd, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def get_controlpanel_adapters(self):
        adapters = getAdapters((self.context, self.request), provided=IControlpanel)
        for name, panel in adapters:
            panel.__name__ = name
            yield name, panel

    def panel_by_name(self, name):
        panels = dict(self.get_controlpanel_adapters())
        return panels.get(name)

    def reply(self):
        if not self.params:
            raise BadRequest("Missing parameter controlpanelname")

        panel = self.panel_by_name(self.params[0])
        res = panel.add(self.params[1:])

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", res["@id"])
        return res
