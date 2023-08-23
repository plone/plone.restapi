from plone.contentrules.rule.interfaces import IRuleAction
from plone.contentrules.rule.interfaces import IRuleCondition
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.controlpanels.interfaces import IContentRulesControlpanel
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.controlpanels import ControlpanelSerializeToJson
from plone.restapi.serializer.controlpanels import SERVICE_ID
from plone.restapi.types import utils
from zope.component import adapter
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer


@implementer(IDexterityContent)
class FakeDXContext:
    """Fake DX content class, so we can re-use the DX field serializers"""


def rule_schema_as_json(schema, request):
    """Build a complete JSON schema for the given controlpanel."""
    context = FakeDXContext()
    fieldsets = utils.get_fieldsets(context, request, schema)

    # Build JSON schema properties
    properties = utils.get_jsonschema_properties(context, request, fieldsets)

    # Determine required fields
    required = []
    for field in utils.iter_fields(fieldsets):
        if field.field.required:
            required.append(field.field.getName())

    # Include field modes
    for field in utils.iter_fields(fieldsets):
        if field.mode:
            properties[field.field.getName()]["mode"] = field.mode

    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "fieldsets": utils.get_fieldset_infos(fieldsets),
    }


@implementer(ISerializeToJson)
@adapter(IContentRulesControlpanel)
class ContentRulesControlpanelSerializeToJson(ControlpanelSerializeToJson):
    def _serialize_schema(self, elements, interface):
        request = self.controlpanel.request
        all_utils = {
            util.title: util for util in getAllUtilitiesRegisteredFor(interface)
        }
        for element in elements:
            element["@schema"] = rule_schema_as_json(
                all_utils[element["title"]].schema, request
            )
        return elements

    def addable_actions(self, manage_elements):
        addable_actions = manage_elements.addable_actions()
        return self._serialize_schema(addable_actions, IRuleAction)

    def addable_conditions(self, manage_elements):
        addable_conditions = manage_elements.addable_conditions()
        return self._serialize_schema(addable_conditions, IRuleCondition)

    def serialize_item(self, proxy):
        manage_elements = queryMultiAdapter(
            (proxy, self.controlpanel.request), name="manage-elements"
        )
        url = self.controlpanel.context.absolute_url()
        name = self.controlpanel.__name__
        proxy_name = proxy.__name__
        return {
            "@id": f"{url}/{SERVICE_ID}/{name}/{proxy_name}",
            "id": proxy_name,
            "title": proxy.title,
            "description": proxy.description,
            "group": self.controlpanel.group,
            "stop": proxy.stop,
            "cascading": proxy.cascading,
            "enabled": proxy.enabled,
            "event": manage_elements.rule_event(),
            "conditions": manage_elements.conditions(),
            "addable_conditions": self.addable_conditions(manage_elements),
            "actions": manage_elements.actions(),
            "addable_actions": self.addable_actions(manage_elements),
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
            rule_id = rule["id"]
            rule["@id"] = f"{portal_url}/@controlpanels/content-rules/{rule_id}"
        json["items"].append(registeredRules)

        return json
