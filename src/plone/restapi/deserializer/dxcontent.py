from .mixins import OrderingMixin
from AccessControl import getSecurityManager
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.deserializer.utils import deserialize_schemas
from z3c.form.interfaces import IManagerValidator
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent


@implementer(IDeserializeFromJson)
@adapter(IDexterityContent, Interface)
class DeserializeFromJson(OrderingMixin):
    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.sm = getSecurityManager()
        self.permission_cache = {}

    def __call__(
        self, validate_all=False, data=None, create=False, mask_validation_errors=True
    ):  # noqa: ignore=C901

        if data is None:
            data = json_body(self.request)

        # Deserialize JSON
        schema_data, errors, modified = deserialize_schemas(
            self.context, self.request, data, validate_all, create
        )

        # Validate schemata
        for schema, field_data in schema_data.items():
            validator = queryMultiAdapter(
                (self.context, self.request, None, schema, None), IManagerValidator
            )
            for error in validator.validate(field_data):
                errors.append({"error": error, "message": error.args[0]})

        if errors:
            if mask_validation_errors:
                # Drop Python specific error classes in order to be able to better handle
                # errors on front-end
                for error in errors:
                    error["error"] = "ValidationError"
            for error in errors:
                error["message"] = translate(error["message"], context=self.request)
            raise BadRequest(errors)

        # We'll set the layout after the validation and even if there
        # are no other changes.
        if "layout" in data:
            layout = data["layout"]
            self.context.setLayout(layout)

        # OrderingMixin
        self.handle_ordering(data)

        if modified and not create:
            descriptions = []
            for interface, names in modified.items():
                descriptions.append(Attributes(interface, *names))
            notify(ObjectModifiedEvent(self.context, *descriptions))

        return self.context
