from plone.dexterity.interfaces import IDexterityContent
from plone.registry.interfaces import IRegistry
from plone.registry.interfaces import IRecordsProxy
from plone.registry.recordsproxy import RecordsProxy
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
from zope.schema.interfaces import IField

import zope.schema


SERVICE_ID = "@controlpanels"

_marker = object()


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
        json_schema = get_jsonschema_for_controlpanel(
            self.controlpanel, self.controlpanel.context, self.controlpanel.request
        )

        # We use a special proxy and check=False just in case the schema has a new field before an upgrade happens
        # Note this doesn't yet handle if a schema field changes type, or the options change
        proxy = self.registry.forInterface(
            self.schema,
            prefix=self.schema_prefix,
            check=False,
            # factory=DefaultRecordsProxy,
        )

        # Temporarily provide IDexterityContent, so we can use DX field
        # serializers
        alsoProvides(proxy, IDexterityContent)

        json_data = {}
        for name, field in zope.schema.getFields(self.schema).items():
            serializer = queryMultiAdapter(
                (field, proxy, self.controlpanel.request), IFieldSerializer
            )
            if serializer:
                value = serializer()
            else:
                value = getattr(proxy, name, None)
            json_data[json_compatible(name)] = value

        noLongerProvides(proxy, IDexterityContent)

        # JSON schema
        return {
            "@id": "{}/{}/{}".format(
                self.controlpanel.context.absolute_url(),
                SERVICE_ID,
                self.controlpanel.__name__,
            ),
            "title": self.controlpanel.title,
            "group": self.controlpanel.group,
            "schema": json_schema,
            "data": json_data,
        }


@implementer(IRecordsProxy)
class DefaultRecordsProxy(RecordsProxy):
    """Modified RecordsProxy which returns defaults if values missing"""

    def __getattr__(self, name):
        if not self.__dict__ or name in self.__dict__.keys():
            return super(RecordsProxy, self).__getattr__(name)
        if name not in self.__schema__:
            raise AttributeError(name)
        value = self.__registry__.get(self.__prefix__ + name, _marker)
        if value is _marker:
            # Instead of returning missing_value we return the default
            # so if this is an upgrade the registry will eventually be
            # set with the default on next save.
            field = self.__schema__[name]
            if IField.providedBy(field):
                field = field.bind(self)
                value = field.default
            else:
                value = self.__schema__[name].default

        return value

    def __setattr__(self, name, value):
        if name in self.__schema__:
            full_name = self.__prefix__ + name
            self.__registry__[full_name] = value
        else:
            self.__dict__[name] = value
