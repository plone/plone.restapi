# -*- coding: utf-8 -*-
from Products.Archetypes.event import ObjectEditedEvent
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces import IObjectPostValidation
from Products.Archetypes.interfaces import IObjectPreValidation
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IFieldDeserializer
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.component import subscribers
from zope.event import notify
from zope.interface import Interface
from zope.interface import implementer

from .mixins import OrderingMixin


@implementer(IDeserializeFromJson)
@adapter(IBaseObject, Interface)
class DeserializeFromJson(OrderingMixin, object):
    """JSON deserializer for Archetypes content types
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, validate_all=False, data=None):
        if data is None:
            data = json_body(self.request)

        obj = self.context
        modified = False

        for field in obj.Schema().fields():
            if not field.writeable(obj):
                continue

            name = field.getName()

            if name in data:
                deserializer = queryMultiAdapter((field, obj, self.request),
                                                 IFieldDeserializer)
                if deserializer is None:
                    continue
                value, kwargs = deserializer(data[name])
                mutator = field.getMutator(obj)
                mutator(value, **kwargs)
                modified = True

        if modified:
            errors = self.validate()
            if not validate_all:
                errors = {f: e for f, e in errors.items() if f in data}
            if errors:
                errors = [{
                    'message': e,
                    'field': f,
                    'error': 'ValidationError'} for f, e in errors.items()]
                raise BadRequest(errors)

            if obj.checkCreationFlag():
                obj.unmarkCreationFlag()
                notify(ObjectInitializedEvent(obj))
                obj.at_post_create_script()
            else:
                notify(ObjectEditedEvent(obj))
                obj.at_post_edit_script()

        # We'll set the layout after the validation and and even if there
        # are no other changes.
        if 'layout' in data:
            layout = data['layout']
            self.context.setLayout(layout)

        # OrderingMixin
        self.handle_ordering(data)

        return obj

    def validate(self):
        # Instead of calling P.Archetypes.BaseObject.validate() we have to
        # provide a custom validation implementation here because some
        # validators extract the field value from the request. However a JSON
        # API request does not contain any form values in the request.
        # Thus we fake a request that extracts form values from the object on
        # demand.

        obj = self.context
        request = ValidationRequest(self.request, obj)
        errors = {}

        obj.pre_validate(request, errors)

        for pre_validator in subscribers((obj,), IObjectPreValidation):
            pre_errors = pre_validator(request)
            if pre_errors is not None:
                for field_name, error_message in pre_errors.items():
                    if field_name in errors:
                        errors[field_name] += " %s" % error_message
                    else:
                        errors[field_name] = error_message

        obj.Schema().validate(instance=obj, REQUEST=None,
                              errors=errors, data=True, metadata=True)

        obj.post_validate(request, errors)

        for post_validator in subscribers((obj,), IObjectPostValidation):
            post_errors = post_validator(request)
            if post_errors is not None:
                for field_name, error_message in post_errors.items():
                    if field_name in errors:
                        errors[field_name] += " %s" % error_message
                    else:
                        errors[field_name] = error_message

        return errors


class ValidationRequest(dict):
    """A fake request for validation purposes.
    """

    def __init__(self, request, context):
        self.request = request
        self.context = context
        self.form = ValidationRequestForm(request, context)

    def __getitem__(self, key):
        if key in self.request:
            return self.request[key]
        return self.form[key]

    def __contains__(self, key):
        return key in self.request or key in self.form

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


class ValidationRequestForm(dict):
    """A request form dict that returns values from the content object.
    """
    def __init__(self, request, context):
        self.request = request
        self.context = context

    def __getitem__(self, key):
        field = self.context.getField(key)
        if field is None:
            return self.request.form[key]

        accessor = field.getEditAccessor(self.context)
        if accessor is None:
            accessor = field.getAccessor(self.context)

        return accessor()

    def __contains__(self, key):
        return key in self.context.Schema()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
