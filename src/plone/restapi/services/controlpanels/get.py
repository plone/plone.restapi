# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.controlpanels import IControlpanel
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapters, getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class ControlpanelsGet(Service):
    controlpanel_name = None

    def publishTraverse(self, request, name):
        self.controlpanel_name = name
        return self

    def get_controlpanels(self):
        return getAdapters(
            (self.context, self.request),
            provided=IControlpanel
        )

    def available_controlpanels(self):
        panels = dict(self.get_controlpanels())
        panels_by_configlet = dict(
            [(p.configlet_id, name) for name, p in panels.items()]
        )

        pctool = getToolByName(self.context, 'portal_controlpanel')
        for group in pctool.getGroups():
            for action_data in pctool.enumConfiglets(group=group['id']):
                name = panels_by_configlet.get(action_data['id'])
                panel = panels.get(name)
                if panel:
                    panel.__name__ = name
                    yield panel

    def panel_by_name(self, name):
        panels = dict(self.get_controlpanels())
        panel = panels.get(name)
        if panel:
            panel.__name__ = name
        return panel

    def reply(self):
        if self.controlpanel_name:
            return self.reply_panel()

        def serialize(panels):
            for panel in panels:
                serializer = ISerializeToJsonSummary(panel)
                yield serializer()

        panels = self.available_controlpanels()
        return IJsonCompatible(list(serialize(panels)))

    def reply_panel(self):
        panel = self.panel_by_name(self.controlpanel_name)
        if panel is None:
            self.request.response.setStatus(404)
            return
        return IJsonCompatible(ISerializeToJson(panel)())
