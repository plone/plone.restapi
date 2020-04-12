# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityFTI
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.controlpanels.interfaces import IDexterityTypesControlpanel
from plone.restapi.serializer.controlpanels import SERVICE_ID
from plone.restapi.serializer.controlpanels import ControlpanelSerializeToJson
from plone.restapi.serializer.controlpanels import get_jsonschema_for_controlpanel
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(IDexterityTypesControlpanel)
class DexterityTypesControlpanelSerializeToJson(ControlpanelSerializeToJson):
    def count(self, portal_type):
        catalog = getToolByName(self.controlpanel.context, 'portal_catalog')
        lengths = dict(
            catalog.Indexes['portal_type'].uniqueValues(withLengths=True))
        return lengths.get(portal_type, 0)

    def serialize_item(self, proxy):
        overview = queryMultiAdapter((proxy, self.controlpanel.request), name='overview')
        form = overview.form_instance
        json_schema = get_jsonschema_for_controlpanel(
            self.controlpanel, self.controlpanel.context, self.controlpanel.request, form
        )

        json_data = {}
        for name, item in form.fields.items():
            serializer = queryMultiAdapter(
                (item.field, proxy.fti, self.controlpanel.request), IFieldSerializer
            )
            if serializer:
                value = serializer()
            else:
                value = getattr(proxy.fti, name, None)
            json_data[json_compatible(name)] = value

        # JSON schema
        return {
            "@id": "{}/{}/{}/{}".format(
                self.controlpanel.context.absolute_url(),
                SERVICE_ID,
                self.controlpanel.__name__,
                proxy.__name__
            ),
            "title": self.controlpanel.title,
            "group": self.controlpanel.group,
            "schema": json_schema,
            "data": json_data,
            "items": []
        }

    def __call__(self, item=None):
        if item is not None:
            return self.serialize_item(item)

        json = super(DexterityTypesControlpanelSerializeToJson, self).__call__()
        json['items'] = []

        portal = getSite()
        portal_url = portal.absolute_url()

        ftis = getAllUtilitiesRegisteredFor(IDexterityFTI)
        for fti in ftis:
            name = fti.__name__
            json['items'].append({
                "@id": "{}/@controlpanels/dexterity-types/{}".format(portal_url, name),
                "@type": name,
                "meta_type": fti.meta_type,
                "id": name,
                "title": fti.Title(),
                "description": fti.Description(),
                "count": self.count(name)
            })
        return json
