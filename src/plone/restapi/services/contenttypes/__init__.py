from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.restapi.types.utils import _deserialize_schema_values
from plone.restapi.types.utils import _format_errors
from plone.restapi.types.utils import _get_jsonschema_for_schema
from plone.restapi.types.utils import _serialize_schema_values
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import iter_fields
from plone.restapi.types.utils import SchemaValues
from plone.restapi.typesettings.manage import count_items
from plone.restapi.typesettings.manage import get_type_settings
from Products.CMFCore.utils import getToolByName
from urllib.parse import quote
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.security import checkPermission

SERVICE_ID = "@content-types"


@implementer(IPublishTraverse)
class ContentTypesService(Service):
    """Base class for @content-types services."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []
        if request.method != "GET":
            alsoProvides(request, IDisableCSRFProtection)

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    @property
    def types_tool(self):
        return getToolByName(self.context, "portal_types")

    def get_fti(self):
        if len(self.params) != 1 or self.params[0] not in self.types_tool:
            raise NotFound("Unknown content type")
        return self.types_tool[self.params[0]]

    def url(self, type_id=None):
        url = f"{self.context.absolute_url()}/{SERVICE_ID}"
        return url if type_id is None else f"{url}/{quote(type_id, safe='')}"

    def json_body(self):
        try:
            return json_body(self.request)
        except DeserializationError as exc:
            raise BadRequest(
                _format_errors([{"message": str(exc), "error": exc}], self.request)
            )

    def raise_errors(self, errors):
        raise BadRequest(_format_errors(errors, self.request))

    def settings(self, fti):
        """Return the settings the current user may manage, with their fields.

        Yields the adapter name, the adapter, its current values, a context
        holding them, and its autoform fieldsets.
        """
        for name, settings in get_type_settings(fti, self.request):
            if settings.permission and not checkPermission(
                settings.permission, self.context
            ):
                continue
            values = settings.read()
            snapshot = SchemaValues(settings.schema, values).__of__(fti)
            fieldsets = get_fieldsets(snapshot, self.request, settings.schema)
            yield name, settings, values, snapshot, fieldsets

    def serialize(self, fti, counts=None, chains=None):
        if counts is None:
            counts = count_items(self.context)
        workflow = getToolByName(self.context, "portal_workflow")
        if chains is None:
            chains = dict(workflow.listChainOverrides())
        properties, required, fieldsets, data = {}, [], [], {}
        for name, settings, values, snapshot, form_fieldsets in self.settings(fti):
            schema = _get_jsonschema_for_schema(
                snapshot, self.request, settings.schema, fieldsets=form_fieldsets
            )
            duplicates = properties.keys() & schema["properties"].keys()
            if duplicates:
                raise ValueError(
                    f"Content type settings {name!r} repeat fields: "
                    f"{', '.join(sorted(duplicates))}"
                )
            properties.update(schema["properties"])
            required.extend(schema["required"])
            fieldsets.append(
                {
                    "id": name,
                    "title": translate(settings.title, context=self.request),
                    "fields": list(schema["properties"]),
                }
            )
            data.update(
                _serialize_schema_values(
                    snapshot, self.request, settings.schema, fieldsets=form_fieldsets
                )
            )
        type_id = fti.getId()
        chain = workflow.getChainFor(type_id)
        return json_compatible(
            {
                "@id": self.url(type_id),
                "id": type_id,
                "title": translate(fti.Title(), context=self.request),
                "items_total": counts.get(type_id, 0),
                "schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "fieldsets": fieldsets,
                },
                "data": data,
                "workflow": {
                    "id": chain[0] if chain else None,
                    "follows_default": chains.get(type_id) is None,
                },
            }
        )

    def update(self, fti, data):
        """Validate all changes, then write them, so updates are atomic."""
        if not isinstance(data, dict):
            self.raise_errors([{"message": "Expected an object", "error": None}])
        errors, updates, known = [], [], set()
        for name, settings, current, snapshot, fieldsets in self.settings(fti):
            fields = {item.field.getName() for item in iter_fields(fieldsets)}
            known |= fields
            supplied = {key: value for key, value in data.items() if key in fields}
            if not supplied:
                continue
            values, field_errors = _deserialize_schema_values(
                fti,
                self.request,
                settings.schema,
                supplied,
                current=current,
                fieldsets=fieldsets,
                strict=True,
            )
            errors.extend(field_errors or settings.validate(values))
            updates.append((settings, values))
        for key in sorted(data.keys() - known):
            errors.append({"field": key, "message": "Unknown field", "error": None})
        if errors:
            self.raise_errors(errors)
        for settings, values in updates:
            settings.write(values)
