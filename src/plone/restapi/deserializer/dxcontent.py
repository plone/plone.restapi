# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IFieldDeserializer
from plone.supermodel.utils import mergedTaggedValueDict
from z3c.form.interfaces import IDataManager
from z3c.form.interfaces import IManagerValidator
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.event import notify
from zope.interface import Interface
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFields
from zope.schema.interfaces import ValidationError
from zope.security.interfaces import IPermission

from .mixins import OrderingMixin


@implementer(IDeserializeFromJson)
@adapter(IDexterityContent, Interface)
class DeserializeFromJson(OrderingMixin, object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.sm = getSecurityManager()
        self.permission_cache = {}

    def __call__(self, validate_all=False):  # noqa: ignore=C901
        data = json_body(self.request)

        modified = False
        schema_data = {}
        errors = []

        for schema in iterSchemata(self.context):
            write_permissions = mergedTaggedValueDict(
                schema, WRITE_PERMISSIONS_KEY)

            for name, field in getFields(schema).items():

                field_data = schema_data.setdefault(schema, {})

                if field.readonly:
                    continue

                if name in data:
                    dm = queryMultiAdapter((self.context, field), IDataManager)
                    if not dm.canWrite():
                        continue

                    if not self.check_permission(write_permissions.get(name)):
                        continue

                    # Deserialize to field value
                    deserializer = queryMultiAdapter(
                        (field, self.context, self.request),
                        IFieldDeserializer)
                    if deserializer is None:
                        continue

                    try:
                        value = deserializer(data[name])
                    except ValueError as e:
                        errors.append({
                            'message': e.message, 'field': name, 'error': e})
                    except ValidationError as e:
                        errors.append({
                            'message': e.doc(), 'field': name, 'error': e})
                    else:
                        field_data[name] = value
                        if value != dm.get():
                            dm.set(value)
                            modified = True

                elif validate_all:
                    # Never validate the changeNote of p.a.versioningbehavior
                    # The Versionable adapter always returns an empty string
                    # which is the wrong type. Should be unicode and should be
                    # fixed in p.a.versioningbehavior
                    if name == 'changeNote':
                        continue
                    dm = queryMultiAdapter((self.context, field), IDataManager)
                    bound = field.bind(self.context)
                    try:
                        bound.validate(dm.get())
                    except ValidationError as e:
                        errors.append({
                            'message': e.doc(), 'field': name, 'error': e})

        # Validate schemata
        for schema, field_data in schema_data.items():
            validator = queryMultiAdapter(
                (self.context, self.request, None, schema, None),
                IManagerValidator)
            for error in validator.validate(field_data):
                errors.append({'error': error, 'message': error.message})

        if errors:
            raise BadRequest(errors)

        # We'll set the layout after the validation and and even if there
        # are no other changes.
        if 'layout' in data:
            layout = data['layout']
            self.context.setLayout(layout)

        # OrderingMixin
        self.handle_ordering(data)

        if modified:
            notify(ObjectModifiedEvent(self.context))

        return self.context

    def check_permission(self, permission_name):
        if permission_name is None:
            return True

        if permission_name not in self.permission_cache:
            permission = queryUtility(IPermission,
                                      name=permission_name)
            if permission is None:
                self.permission_cache[permission_name] = True
            else:
                self.permission_cache[permission_name] = bool(
                    self.sm.checkPermission(permission.title, self.context))
        return self.permission_cache[permission_name]
