from Acquisition import ImplicitAcquisitionWrapper
from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry
from plone.restapi.behaviors import IBlocks
from plone.restapi.controlpanels import IControlpanel
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.types import utils
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides

import zope.schema


SERVICE_ID = "@controlpanels"

# Same class is in deserializer. Should centralise it.
@implementer(IDexterityContent, IBlocks)
class FakeDXContext:
    """Fake DX content class, so we can re-use the DX field deserializers"""


@implementer(ISerializeToJsonSummary)
@adapter(IControlpanel)
class ControlpanelSummarySerializeToJson:
    def __init__(self, controlpanel):
        self.controlpanel = controlpanel

    def __call__(self):
        return {
            "@id": "{}/{}/{}".format(
                self.controlpanel.context.absolute_url(),
                SERVICE_ID,
                self.controlpanel.__name__,
            ),
            "title": self.controlpanel.title,
            "group": self.controlpanel.group,
        }


def get_jsonschema_for_controlpanel(controlpanel, context, request, form=None):
    """Build a complete JSON schema for the given controlpanel."""
    if not form:
        schema = controlpanel.schema
        fieldsets = utils.get_fieldsets(context, request, schema)
    else:
        fieldsets = utils.get_form_fieldsets(form)

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

            # Make a fake context and copy registry values onto it
            fake_context = FakeDXContext()

                    
            # Copy all field values from the proxy to the fake context
            #   so that field serializers can properly adapt the context
            for name in zope.schema.getFields(self.schema).keys():
                setattr(fake_context, name, getattr(proxy, name, None))
            alsoProvides(fake_context, self.schema)

            wrapped_context = ImplicitAcquisitionWrapper(fake_context, self.controlpanel.context)

            json_data = {}
            for name, field in zope.schema.getFields(self.schema).items():
                serializer = queryMultiAdapter(
                    (field, wrapped_context, self.controlpanel.request), IFieldSerializer
                )
                if serializer:
                    value = serializer()
                else:
                    value = getattr(proxy, name, None)
                json_data[json_compatible(name)] = value

            noLongerProvides(proxy, IDexterityContent)

            result["data"] = json_data

        return result
