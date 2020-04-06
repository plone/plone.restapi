# -*- coding: utf-8 -*-
from zExceptions import BadRequest
from plone.i18n.normalizer import idnormalizer
from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.controlpanels import ControlpanelDeserializeFromJson
from plone.restapi.controlpanels.interfaces import IDexterityTypesControlpanel
from plone.restapi.interfaces import IDeserializeFromJson
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import alsoProvides

import plone.protect.interfaces

@implementer(IDeserializeFromJson)
@adapter(IDexterityTypesControlpanel)
class DexterityTypesControlpanelDeserializeFromJson(ControlpanelDeserializeFromJson):

    def add(self):
        data = json_body(self.request)

        title = data.get("title", None)
        if not title:
            raise BadRequest("Property 'title' is required")

        tid = data.get("id", None)
        if not tid:
            tid = idnormalizer.normalize(title).replace("-", "_")

        description = data.get("description", "")

        properties = {
            "id": tid,
            "title": title,
            "description": description
        }

        # # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        context = queryMultiAdapter((self.context, self.request), name='dexterity-types')
        add_type = queryMultiAdapter((context, self.request), name='add-type')
        fti = add_type.form_instance.create(data=properties)
        add_type.form_instance.add(fti)

    def __call__(self):
        if self.request.method.lower() == 'post':
            return self.add()
        return super(DexterityTypesControlpanelDeserializeFromJson, self).__call__()
