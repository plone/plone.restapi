# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityFTI
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.controlpanels.interfaces import IDexterityTypesControlpanel
from plone.restapi.serializer.controlpanels import ControlpanelSerializeToJson
from zope.component import adapter
from zope.component import getAllUtilitiesRegisteredFor
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

    def __call__(self):
        json = super(DexterityTypesControlpanelSerializeToJson, self).__call__()
        json['items'] = []

        portal = getSite()
        portal_url = portal.absolute_url()

        ftis = getAllUtilitiesRegisteredFor(IDexterityFTI)
        for fti in ftis:
            name = fti.__name__
            json['items'].append({
                "@id": "{}/controlpanel/dexterity-types/{}".format(portal_url, name),
                "@type": fti.name,
                "meta_type": fti.meta_type,
                "id": name,
                "title": fti.Title(),
                "description": fti.Description(),
                "count": self.count(name)
            })
        return json
