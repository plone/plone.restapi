from plone.restapi.controlpanels import IControlpanel
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapters
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class ControlpanelsGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def get_controlpanel_adapters(self):
        adapters = getAdapters((self.context, self.request), provided=IControlpanel)
        for name, panel in adapters:
            panel.__name__ = name
            yield name, panel

    def available_controlpanels(self):
        panels = dict(self.get_controlpanel_adapters())
        panels_by_configlet = {p.configlet_id: name for name, p in panels.items()}

        pctool = getToolByName(self.context, "portal_controlpanel")
        for group in pctool.getGroups():
            for action_data in pctool.enumConfiglets(group=group["id"]):
                name = panels_by_configlet.get(action_data["id"])
                panel = panels.get(name)
                if panel:
                    yield panel

    def panel_by_name(self, name):
        panels = dict(self.get_controlpanel_adapters())
        return panels.get(name)

    def reply(self):
        if self.params:
            return self.reply_panel()

        def serialize(panels):
            for panel in panels:
                serializer = ISerializeToJsonSummary(panel)
                yield serializer()

        # List panels
        panels = self.available_controlpanels()
        return IJsonCompatible(list(serialize(panels)))

    def reply_panel(self):
        name = self.params[0]
        panel = self.panel_by_name(name)
        if panel is None:
            self.request.response.setStatus(404)
            return

        # Panel child request
        if len(self.params) > 1:
            return IJsonCompatible(panel.get(self.params[1:]))

        # Panel request
        return IJsonCompatible(ISerializeToJson(panel)())
