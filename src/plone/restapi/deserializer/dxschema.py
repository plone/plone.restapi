from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi import _
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import ISchemaDeserializer
from plone.restapi.permissions import check_permission
from plone.supermodel.utils import mergedTaggedValueDict
from z3c.form.interfaces import IDataManager
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from zope.schema.interfaces import ValidationError
from zope.interface.interfaces import IInterface


@implementer(ISchemaDeserializer)
@adapter(IInterface, IDexterityContent, Interface)
class DeserializeFromJson:
    def __init__(self, schema, context, request):
        self.schema = schema
        self.context = context
        self.request = request
        self.permission_cache = {}
        self.modified = {}

    def mark_field_as_changed(self, schema, fieldname):
        """Collect the names of the modified fields. Use prefixed name because
        z3c.form does so.
        """

        prefixed_name = f"{schema.__name__}.{fieldname}"
        self.modified.setdefault(schema, []).append(prefixed_name)

    def __call__(self, data, validate_all, create=False) -> tuple[dict, list, dict]:
        schema = self.schema
        schema_data = {}
        errors = []
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

                if not check_permission(
                    write_permissions.get(name), self.context, self.permission_cache
                ):
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

        return schema_data, errors, self.modified
