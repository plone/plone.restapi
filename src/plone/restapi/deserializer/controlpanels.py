# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from plone.restapi.controlpanels import IControlpanel
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer


@implementer(IDeserializeFromJson)
@adapter(IControlpanel)
class ControlpanelDeserializeFromJson(object):

    def __init__(self, controlpanel):
        self.controlpanel = controlpanel
        self.schema = self.controlpanel.registry_schema

        self.registry = getUtility(IRegistry)

    def __call__(self):
        data = json_body(self.controlpanel.request)
        proxy = self.registry.forInterface(self.schema, prefix='plone')
        for key, value in data.items():
            setattr(proxy, key, value)
