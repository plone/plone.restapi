# -*- coding: utf-8 -*-
from Products.Archetypes.event import ObjectEditedEvent
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.interfaces import IBaseObject
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IFieldDeserializer
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import Interface
from zope.interface import implementer


@implementer(IDeserializeFromJson)
@adapter(IBaseObject, Interface)
class DeserializeFromJson(object):
    """JSON deserializer for Archetypes content types
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, validate_all=False):
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
                mutator = field.getMutator(obj, **kwargs)
                mutator(value)
                modified = True

        if modified:
            errors = obj.validate(data=True, metadata=True)
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

        return obj
