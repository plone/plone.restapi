# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces.field import IField
from Products.Archetypes.interfaces.field import IFileField
from Products.Archetypes.interfaces.field import IImageField
from Products.Archetypes.interfaces.field import IReferenceField
from Products.Archetypes.interfaces.field import ITextField
from plone.app.blob.interfaces import IBlobField
from plone.app.blob.interfaces import IBlobImageField
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from archetypes.querywidget.interfaces import IQueryField


@adapter(IField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class DefaultFieldSerializer(object):

    def __init__(self, field, context, request):
        self.context = context
        self.request = request
        self.field = field

    def __call__(self):
        accessor = self.field.getEditAccessor(self.context)
        if accessor is None:
            accessor = self.field.getAccessor(self.context)
        return json_compatible(accessor())


@adapter(IFileField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class FileFieldSerializer(DefaultFieldSerializer):

    def __call__(self):
        url = '/'.join((self.context.absolute_url(),
                        '@@download',
                        self.field.getName()))
        return json_compatible(url)


@adapter(ITextField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class TextFieldSerializer(DefaultFieldSerializer):

    def __call__(self):
        return {
            'content-type': json_compatible(
                self.field.getContentType(self.context)),
            'data': super(TextFieldSerializer, self).__call__()
        }


@adapter(IImageField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class ImageFieldSerializer(DefaultFieldSerializer):

    def __call__(self):
        url = '/'.join((self.context.absolute_url(),
                        '@@images',
                        self.field.getName()))
        return json_compatible(url)


@adapter(IBlobField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class BlobFieldSerializer(FileFieldSerializer):
    pass


@adapter(IBlobImageField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class BlobImageFieldSerializer(ImageFieldSerializer):
    pass


@adapter(IReferenceField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class ReferenceFieldSerializer(DefaultFieldSerializer):

    def __call__(self):
        accessor = self.field.getAccessor(self.context)
        refs = accessor()
        if self.field.multiValued:
            return [json_compatible(r.absolute_url()) for r in refs]
        else:
            if refs is None:
                return None
            return json_compatible(refs.absolute_url())


@adapter(IQueryField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class QueryFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        raw_value = self.field.getRaw(self.context)
        return json_compatible(map(dict, raw_value))
