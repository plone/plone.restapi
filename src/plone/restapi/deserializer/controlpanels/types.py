# -*- coding: utf-8 -*-
from plone.restapi.controlpanels.interfaces import IDexterityTypesControlpanel
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.controlpanels import ControlpanelDeserializeFromJson
from plone.restapi.interfaces import IDeserializeFromJson
from zope.component import adapter, queryMultiAdapter
from zope.interface import implementer


@implementer(IDeserializeFromJson)
@adapter(IDexterityTypesControlpanel)
class DexterityTypesControlpanelDeserializeFromJson(ControlpanelDeserializeFromJson):
    def deserialize_item(self, proxy):
        data = json_body(self.request)
        overview = queryMultiAdapter((proxy, self.request), name="overview")
        overview.form_instance.applyChanges(data)
        behaviors = queryMultiAdapter((proxy, self.request), name="behaviors")
        behaviors.form_instance.applyChanges(data)

    def __call__(self, item=None):
        if item is not None:
            return self.deserialize_item(item)
        return super(DexterityTypesControlpanelDeserializeFromJson, self).__call__()
