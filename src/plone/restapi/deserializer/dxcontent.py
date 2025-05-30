from .mixins import OrderingMixin
from AccessControl import getSecurityManager
from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.restapi import _
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.serializer.schema import _check_permission
from plone.supermodel.utils import mergedTaggedValueDict
from z3c.form.interfaces import IDataManager
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
from zope.schema import getFields
from zope.schema.interfaces import ValidationError


@implementer(IDeserializeFromJson)
@adapter(IDexterityContent, Interface)
class DeserializeFromJson(OrderingMixin):
    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.sm = getSecurityManager()
        self.permission_cache = {}
        self.modified = {}

    def __call__(
        self, validate_all=False, data=None, create=False, mask_validation_errors=True
    ):  # noqa: ignore=C901

        if data is None:
            data = json_body(self.request)

        schema_data, errors = self.get_schema_data(data, validate_all, create)

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

        if self.modified and not create:
            descriptions = []
            for interface, names in self.modified.items():
                descriptions.append(Attributes(interface, *names))
            notify(ObjectModifiedEvent(self.context, *descriptions))

        return self.context

    def get_schema_data(self, data, validate_all, create=False):
        schema_data = {}
        errors = []

        for schema in iterSchemata(self.context):
            write_permissions = mergedTaggedValueDict(schema, WRITE_PERMISSIONS_KEY)

            for name, field in getFields(schema).items():
                __traceback_info__ = f"field={field}"

                field_data = schema_data.setdefault(schema, {})

                if field.readonly:
                    continue

                if name in data:
                    dm = queryMultiAdapter((self.context, field), IDataManager)
                    if not dm.canWrite():
                        continue

                    if not self.check_permission(write_permissions.get(name)):
                        continue

                    # set the field to missing_value if we receive null
                    if data[name] is None:
                        if not field.required:
                            if dm.get():
                                self.mark_field_as_changed(schema, name)
                            dm.set(field.missing_value)
                        else:
                            errors.append(
                                {
                                    "field": field.__name__,
                                    "message": _(
                                        "${field_name} is a required field."
                                        " Setting it to null is not allowed.",
                                        mapping={"field_name": field.__name__},
                                    ),
                                }
                            )
                        continue

                    # Deserialize to field value
                    deserializer = queryMultiAdapter(
                        (field, self.context, self.request), IFieldDeserializer
                    )
                    if deserializer is None:
                        continue

                    try:
                        value = deserializer(data[name])
                    except ValueError as e:
                        errors.append({"message": str(e), "field": name, "error": e})
                    except ValidationError as e:
                        errors.append({"message": e.doc(), "field": name, "error": e})
                    else:
                        field_data[name] = value
                        current_value = dm.get()
                        if value != current_value:
                            should_change = True
                        elif create and dm.field.defaultFactory:
                            # During content creation we should set the value even if
                            # it is the same from the dm if the current_value was
                            # returned from a default_factory method
                            should_change = (
                                dm.field.defaultFactory(self.context) == current_value
                            )
                        else:
                            should_change = False

                        if should_change:
                            dm.set(value)
                            self.mark_field_as_changed(schema, name)

                elif validate_all:
                    # Never validate the changeNote of p.a.versioningbehavior
                    # The Versionable adapter always returns an empty string
                    # which is the wrong type. Should be unicode and should be
                    # fixed in p.a.versioningbehavior
                    if name == "changeNote":
                        continue
                    dm = queryMultiAdapter((self.context, field), IDataManager)
                    bound = field.bind(self.context)
                    try:
                        bound.validate(dm.get())
                    except ValidationError as e:
                        errors.append({"message": e.doc(), "field": name, "error": e})

        return schema_data, errors

    def mark_field_as_changed(self, schema, fieldname):
        """Collect the names of the modified fields. Use prefixed name because
        z3c.form does so.
        """

        prefixed_name = schema.__name__ + "." + fieldname
        self.modified.setdefault(schema, []).append(prefixed_name)

    def check_permission(self, permission_name):
        # Here for backwards-compatibility
        return _check_permission(permission_name, self)
