from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry
from plone.restapi.controlpanels import IControlpanel
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.types import utils
from zope.component import adapter
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides

SERVICE_ID = "@controlpanels"


@implementer(ISerializeToJsonSummary)
@adapter(IControlpanel)
class ControlpanelSummarySerializeToJson:
    def __init__(self, controlpanel):
        self.controlpanel = controlpanel

    def __call__(self):
        result = {
            "@id": "{}/{}/{}".format(
                self.controlpanel.context.absolute_url(),
                SERVICE_ID,
                self.controlpanel.__name__,
            ),
            "title": self.controlpanel.title,
            "group": self.controlpanel.group,
        }

        if hasattr(self.controlpanel, "get_searchable_text"):
            result["searchable_text"] = self.controlpanel.get_searchable_text()
        else:
            if self.controlpanel.title:
                result["searchable_text"] = [
                    self.controlpanel.title,
                    self.controlpanel.description,
                ]

        return result


def get_jsonschema_for_controlpanel(controlpanel, context, request, form=None):
    """Build a complete JSON schema for the given controlpanel."""
    fieldsets = utils.get_form_fieldsets(form) if form else None
    return utils._get_jsonschema_for_schema(
        context, request, controlpanel.schema, fieldsets=fieldsets
    )


@implementer(ISerializeToJson)
@adapter(IControlpanel)
class ControlpanelSerializeToJson:
    def __init__(self, controlpanel):
        self.controlpanel = controlpanel
        self.schema = self.controlpanel.schema
        self.schema_prefix = self.controlpanel.schema_prefix

        self.registry = getUtility(IRegistry)

    def __call__(self):
        result = {
            "@id": "{}/{}/{}".format(
                self.controlpanel.context.absolute_url(),
                SERVICE_ID,
                self.controlpanel.__name__,
            ),
            "title": self.controlpanel.title,
            "group": self.controlpanel.group,
        }

        if self.schema is not None:
            json_schema = get_jsonschema_for_controlpanel(
                self.controlpanel, self.controlpanel.context, self.controlpanel.request
            )
            result["schema"] = json_schema

            proxy = self.registry.forInterface(self.schema, prefix=self.schema_prefix)

            # Temporarily provide IDexterityContent, so we can use DX field
            # serializers
            alsoProvides(proxy, IDexterityContent)
            json_data = utils._serialize_schema_values(
                proxy, self.controlpanel.request, self.schema
            )
            noLongerProvides(proxy, IDexterityContent)

            result["data"] = json_data

        return result
