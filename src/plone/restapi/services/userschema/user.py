from plone.app.users.browser.register import getRegisterSchema
from plone.app.users.browser.userdatapanel import getUserDataSchema
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.restapi.types.utils import get_fieldset_infos
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_properties
from plone.restapi.types.utils import iter_fields
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class UserSchemaGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@userschema as parameters
        self.params.append(name)
        return self

    def build_userschema_as_jsonschema(self, user_schema):
        """function to build a jsonschema from user schema information"""
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

    def reply(self):
        if len(self.params) == 0:
            return self.build_userschema_as_jsonschema(getUserDataSchema())
        elif len(self.params) == 1 and self.params[0] == "registration":
            return self.build_userschema_as_jsonschema(getRegisterSchema())

        self.request.response.setStatus(400)
        return dict(
            error=dict(
                type="Invalid parameters",
                message="Parameters supplied are not valid.",
            )
        )
