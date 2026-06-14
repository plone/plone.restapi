from plone.restapi.controlpanels.interfaces import IControlpanel
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer
from zope.publisher.interfaces import NotFound

import zope.schema


@implementer(IControlpanel)
class RegistryConfigletPanel:
    configlet = None
    configlet_id = None
    configlet_category_id = None
    schema = None

    schema_prefix = "plone"

    def _get_configlet(self):
        configlet_data = self.portal_cp.enumConfiglets(self.configlet_category_id)
        for action in configlet_data:
            if action["id"] == self.configlet_id:
                return action

    def _get_group_title(self):
        groups = [
            g
            for g in self.portal_cp.getGroups()
            if g["id"] == self.configlet["category"]
        ]
        return [g["title"] for g in groups][0]

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.portal_cp = getToolByName(self.context, "portal_controlpanel")

        self.configlet = self._get_configlet()
        if self.configlet:
            self.title = self.configlet["title"]
            self.group = self._get_group_title()

    def get_searchable_text(self):

        text_parts = []

        if self.title:
            text_parts.append(self.title)

        if self.group:
            text_parts.append(self.group)

        if self.schema is not None:
            for name, field in zope.schema.getFields(self.schema).items():
                if field.title:
                    text_parts.append(field.title)

        return [text for text in text_parts if text]

    def add(self, names):
        raise NotFound(self.context, names, self.request)

    def get(self, names):
        raise NotFound(self.context, names, self.request)

    def update(self, names):
        raise NotFound(self.context, names, self.request)

    def delete(self, names):
        raise NotFound(self.context, names, self.request)
