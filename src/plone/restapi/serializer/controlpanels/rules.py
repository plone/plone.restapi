from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.controlpanels.interfaces import IContentRulesControlpanel
from plone.restapi.serializer.controlpanels import SERVICE_ID
from plone.restapi.serializer.controlpanels import ControlpanelSerializeToJson
from zope.component import adapter
from zope.component.hooks import getSite
from zope.component import queryMultiAdapter
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(IContentRulesControlpanel)
class ContentRulesControlpanelSerializeToJson(ControlpanelSerializeToJson):
    def serialize_item(self, proxy):
        manage_elements = queryMultiAdapter(
            (proxy, self.controlpanel.request), name="manage-elements"
        )
        return {
            "@id": "{}/{}/{}/{}".format(
                self.controlpanel.context.absolute_url(),
                SERVICE_ID,
                self.controlpanel.__name__,
                proxy.__name__,
            ),
            "id": proxy.__name__,
            "title": proxy.title,
            "description": proxy.description,
            "group": self.controlpanel.group,
            "stop": proxy.stop,
            "cascading": proxy.cascading,
            "enabled": proxy.enabled,
            "event": manage_elements.rule_event(),
            "conditions": manage_elements.conditions(),
            "addable_conditions": manage_elements.addable_conditions(),
            "actions": manage_elements.actions(),
            "addable_actions": manage_elements.addable_actions(),
            "assignments": manage_elements.assignments(),
        }

    def __call__(self, item=None):
        if item is not None:
            return self.serialize_item(item)

        json = super().__call__()
        json["items"] = []

        portal = getSite()
        portal_url = portal.absolute_url()
        context = self.controlpanel.context
        request = self.controlpanel.request

        cpanel = queryMultiAdapter((context, request), name="rules-controlpanel")
        registeredRules = cpanel.registeredRules()

        for rule in registeredRules:
            rule["@id"] = "{}/@controlpanels/content-rules/{}".format(
                portal_url, rule["id"]
            )
        json["items"].append(registeredRules)

        return json
