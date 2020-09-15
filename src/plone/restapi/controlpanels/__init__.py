# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.publisher.interfaces import NotFound
from plone.restapi.controlpanels.interfaces import IControlpanel
from Products.CMFCore.utils import getToolByName


@implementer(IControlpanel)
class RegistryConfigletPanel(object):
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

    def add(self, names):
        raise NotFound(self.context, names, self.request)

    def get(self, names):
        raise NotFound(self.context, names, self.request)

    def update(self, names):
        raise NotFound(self.context, names, self.request)

    def delete(self, names):
        raise NotFound(self.context, names, self.request)
