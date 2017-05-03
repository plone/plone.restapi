from plone.restapi.controlpanels import IControlpanel
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.types import utils
from plone.registry.interfaces import IRegistry
from zope.interface import implementer, Interface
from zope.component import adapter, getMultiAdapter, queryMultiAdapter, getUtility

import zope.schema


@implementer(ISerializeToJsonSummary)
@adapter(IControlpanel)
class ControlpanelSummarySerializeToJson(object):

    def __init__(self, controlpanel):
        self.controlpanel = controlpanel

    def __call__(self):
        return {
            '@id': '{}/@controlpanel/{}'.format(
                self.controlpanel.context.absolute_url(),
                self.controlpanel.__name__
            ),
            'title': self.controlpanel.title,
            'group': self.controlpanel.group,
        }


def get_jsonschema_for_controlpanel(controlpanel, context, request, excluded_fields=None):
    """Build a complete JSON schema for the given FTI.
    """
    if excluded_fields is None:
        excluded_fields = []

    schema = controlpanel.registry_schema

    fieldsets = utils.get_fieldsets(context, request, schema)

    # Build JSON schema properties
    properties = utils.get_jsonschema_properties(
        context, request, fieldsets, excluded_fields=excluded_fields)

    # Determine required fields
    required = []
    for field in utils.iter_fields(fieldsets):
        if field.field.required:
            required.append(field.field.getName())

    # Include field modes
    for field in utils.iter_fields(fieldsets):
        if field.mode:
            properties[field.field.getName()]['mode'] = field.mode

    return {
        'type': 'object',
        'properties': properties,
        'required': required,
        'fieldsets': utils.get_fieldset_infos(fieldsets),
    }


@implementer(ISerializeToJson)
@adapter(IControlpanel)
class ControlpanelSerializeToJson(object):

    def __init__(self, controlpanel):
        self.controlpanel = controlpanel
        self.schema = self.controlpanel.registry_schema

        self.registry = getUtility(IRegistry)

    def __call__(self):
        json_schema = get_jsonschema_for_controlpanel(
            self.controlpanel,
            self.controlpanel.context,
            self.controlpanel.request
        )

        proxy = self.registry.forInterface(self.schema, prefix='plone')

        json_data = {}
        for name, field in zope.schema.getFields(self.schema).items():
            serializer = queryMultiAdapter(
                (field, proxy, self.controlpanel.request),
                IFieldSerializer
            )
            if serializer:
                value = serializer()
            else:
                value = getattr(proxy, name, None)
            json_data[json_compatible(name)] = value

        # JSON schema
        return {
            '@id': '{}/@controlpanel/{}'.format(
                self.controlpanel.context.absolute_url(),
                self.controlpanel.__name__
            ),
            'title': self.controlpanel.title,
            'group': self.controlpanel.group,
            'schema': json_schema,
            'data': json_data,
        }
