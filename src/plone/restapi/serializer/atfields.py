# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces.field import IField
from Products.Archetypes.interfaces.field import IFileField
from Products.Archetypes.interfaces.field import IImageField
from Products.Archetypes.interfaces.field import IReferenceField
from Products.Archetypes.interfaces.field import ITextField
from Products.CMFCore.interfaces import IPropertiesTool
from plone.app.blob.interfaces import IBlobField
from plone.app.blob.interfaces import IBlobImageField
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import implementer


try:
    from Products.CMFPlone.factory import _IMREALLYPLONE5  # noqa
except ImportError:
    PLONE_5 = False  # pragma: no cover
else:
    PLONE_5 = True  # pragma: no cover


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
        result = {
            'filename': self.field.getFilename(self.context),
            'content-type': self.field.getContentType(self.context),
            'size': self.field.get_size(self.context),
            'download': url
        }
        return json_compatible(result)


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
        image = self.field.get(self.context)
        if not image:
            return None

        scales = self.get_scales()
        download_url = scales.pop('original')
        result = {
            'filename': self.field.getFilename(self.context),
            'content-type': self.field.getContentType(self.context),
            'size': self.field.get_size(self.context),
            'download': download_url,
            'scales': scales,
        }
        return json_compatible(result)

    def get_scales(self):
        absolute_url = self.context.absolute_url()
        scales = {name: '{0}/@@images/image/{1}'.format(absolute_url, name)
                  for name in self.get_scale_names()}
        scales['original'] = '/'.join((
            absolute_url, '@@images', self.field.getName()))
        return scales

    def get_scale_names(self):
        if PLONE_5:
            from plone.registry.interfaces import IRegistry
            registry = getUtility(IRegistry)
            from Products.CMFPlone.interfaces import IImagingSchema
            imaging_settings = registry.forInterface(
                IImagingSchema,
                prefix='plone'
            )
            allowed_sizes = imaging_settings.allowed_sizes

        else:
            ptool = getUtility(IPropertiesTool)
            image_properties = ptool.imaging_properties
            allowed_sizes = image_properties.getProperty('allowed_sizes')

        return [size.split(' ')[0] for size in allowed_sizes]


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
