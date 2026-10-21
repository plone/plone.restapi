from plone.registry.interfaces import IRegistry
from plone.restapi.controlpanels import IControlpanel
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.types.utils import _deserialize_schema_values
from plone.restapi.types.utils import _format_errors
from plone.restapi.types.utils import SchemaValues
from z3c.form.interfaces import IManagerValidator
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implementer

# BBB
FakeDXContext = SchemaValues


@implementer(IDeserializeFromJson)
@adapter(IControlpanel)
class ControlpanelDeserializeFromJson:
    def __init__(self, controlpanel):
        self.controlpanel = controlpanel
        self.schema = self.controlpanel.schema
        self.schema_prefix = self.controlpanel.schema_prefix

        self.registry = getUtility(IRegistry)

        self.context = self.controlpanel.context
        self.request = self.controlpanel.request

    def __call__(self, mask_validation_errors=True):
        if self.schema is None:
            return

        data = json_body(self.controlpanel.request)

        proxy = self.registry.forInterface(self.schema, prefix=self.schema_prefix)

        values, errors = _deserialize_schema_values(
            self.context, self.request, self.schema, data
        )
        for name, value in values.items():
            setattr(proxy, name, value)

        # Validate schemata
        validator = queryMultiAdapter(
            (self.context, self.request, None, self.schema, None), IManagerValidator
        )
        for error in validator.validate(values):
            errors.append({"error": error, "message": str(error)})

        if errors:
            raise BadRequest(
                _format_errors(errors, self.request, mask=mask_validation_errors)
            )
