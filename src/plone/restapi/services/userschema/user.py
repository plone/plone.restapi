# -*- coding: utf-8 -*-
from plone.app.users.browser.userdatapanel import getUserDataSchema
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.restapi.types.utils import get_fieldset_infos, get_fieldsets, get_jsonschema_properties, iter_fields
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class RegistrationUserSchemaGet(Service):
    def reply(self):
        registry = getUtility(IRegistry)
        visibility_settings = registry.get("plone.userfield_visibility", {})

        user_schema = getUserDataSchema()
        fieldsets = get_fieldsets(self.context, self.request, user_schema)

        properties = get_jsonschema_properties(self.context, self.request, fieldsets)
        required = [field.field.getName() for field in iter_fields(fieldsets) if field.field.required]

        # Filter only registration fields
        properties = {
            field.field.getName(): properties[field.field.getName()]
            for field in iter_fields(fieldsets)
            if visibility_settings.get(field.field.getName(), "both") in ["registration", "both"]
        }
        required = [field for field in required if field in properties]

        return {
            "type": "object",
            "properties": json_compatible(properties),
            "required": required,
            "fieldsets": get_fieldset_infos(fieldsets),
        }
