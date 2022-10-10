# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from plone.restapi.types.utils import get_jsonschema_properties
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_fieldset_infos
from plone.restapi.types.utils import iter_fields
from plone.app.users.browser.userdatapanel import getUserDataSchema
from plone.restapi.serializer.converters import json_compatible


class UserSchemaGet(Service):
    def reply(self):
        user_schema = getUserDataSchema()
        fieldsets = get_fieldsets(self.context, self.request, user_schema)

        # Build JSON schema properties
        properties = get_jsonschema_properties(self.context, self.request, fieldsets)

        # Determine required fields
        required = []
        for field in iter_fields(fieldsets):
            if field.field.required:
                required.append(field.field.getName())

        # Include field modes
        for field in iter_fields(fieldsets):
            if field.mode:
                properties[field.field.getName()]["mode"] = field.mode

        return {
            "type": "object",
            "properties": json_compatible(properties),
            "required": required,
            "fieldsets": get_fieldset_infos(fieldsets),
        }
