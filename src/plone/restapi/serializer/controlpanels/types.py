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
from zope.i18n import translate


@implementer(ISerializeToJson)
@adapter(IDexterityTypesControlpanel)
class DexterityTypesControlpanelSerializeToJson(ControlpanelSerializeToJson):
    def count(self, portal_type):
        catalog = getToolByName(self.controlpanel.context, "portal_catalog")
        lengths = dict(catalog.Indexes["portal_type"].uniqueValues(withLengths=True))
        return lengths.get(portal_type, 0)

    def serialize_item(self, proxy):
        json_data = {}
        json_schema = {}
        fti = proxy.fti

        overview = queryMultiAdapter(
            (proxy, self.controlpanel.request), name="overview"
        )
        form = overview.form_instance
        json_schema = get_jsonschema_for_controlpanel(
            self.controlpanel,
            self.controlpanel.context,
            self.controlpanel.request,
            form,
        )

        for name, item in form.fields.items():
            serializer = queryMultiAdapter(
                (item.field, fti, self.controlpanel.request), IFieldSerializer
            )
            if serializer:
                value = serializer()
            else:
                value = getattr(fti, name, None)
            json_data[json_compatible(name)] = value

        behaviors = queryMultiAdapter(
            (proxy, self.controlpanel.request), name="behaviors"
        )
        form = behaviors.form_instance
        behaviors_schema = get_jsonschema_for_controlpanel(
            self.controlpanel,
            self.controlpanel.context,
            self.controlpanel.request,
            form,
        )

        behaviors_schema["fieldsets"][0]["id"] = "behaviors"
        behaviors_schema["fieldsets"][0]["title"] = translate(
            "Behaviors", domain="plone", context=self.controlpanel.request
        )
        json_schema["fieldsets"].extend(behaviors_schema["fieldsets"])
        json_schema["properties"].update(behaviors_schema["properties"])

        for name, item in form.fields.items():
            behaviors = getattr(fti, "behaviors", [])
            json_data[json_compatible(name)] = name in behaviors

        # JSON schema
        return {
            "@id": "{}/{}/{}/{}".format(
                self.controlpanel.context.absolute_url(),
                SERVICE_ID,
                self.controlpanel.__name__,
                proxy.__name__,
            ),
            "title": fti.Title(),
            "description": fti.Description(),
            "group": self.controlpanel.group,
            "schema": json_schema,
            "data": json_data,
            "items": [],
        }

    def __call__(self, item=None):
        if item is not None:
            return self.serialize_item(item)

        json = super().__call__()
        json["items"] = []

        portal = getSite()
        portal_url = portal.absolute_url()

        ftis = getAllUtilitiesRegisteredFor(IDexterityFTI)
        for fti in ftis:
            name = fti.__name__
            json["items"].append(
                {
                    "@id": "{}/@controlpanels/dexterity-types/{}".format(
                        portal_url, name
                    ),
                    "@type": name,
                    "meta_type": fti.meta_type,
                    "id": name,
                    "title": fti.Title(),
                    "description": fti.Description(),
                    "count": self.count(name),
                }
            )
        return json
