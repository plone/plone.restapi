# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.interfaces import INamedFileField
from plone.namedfile.interfaces import INamedImageField
from plone.restapi.imaging import get_scales
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IField


@adapter(IField, IDexterityContent, Interface)
@implementer(IFieldSerializer)
class DefaultFieldSerializer(object):

    def __init__(self, field, context, request):
        self.context = context
        self.request = request
        self.field = field

    def __call__(self):
        return json_compatible(self.get_value())

    def get_value(self, default=None):
        return getattr(self.field.interface(self.context),
                       self.field.__name__,
                       default)


@adapter(INamedImageField, IDexterityContent, Interface)
class ImageFieldSerializer(DefaultFieldSerializer):

    def __call__(self):
        image = self.field.get(self.context)
        if not image:
            return None

        url = '/'.join((self.context.absolute_url(),
                        '@@images',
                        self.field.__name__))

        width, height = image.getImageSize()
        scales = get_scales(self.context, self.field, width, height)
        result = {
            'filename': image.filename,
            'content-type': image.contentType,
            'size': image.getSize(),
            'download': url,
            'width': width,
            'height': height,
            'scales': scales
        }
        return json_compatible(result)


@adapter(INamedFileField, IDexterityContent, Interface)
class FileFieldSerializer(DefaultFieldSerializer):

    def __call__(self):
        namedfile = self.field.get(self.context)
        if namedfile is None:
            return None

        url = '/'.join((self.context.absolute_url(),
                        '@@download',
                        self.field.__name__))
        result = {
            'filename': namedfile.filename,
            'content-type': namedfile.contentType,
            'size': namedfile.getSize(),
            'download': url
        }
        return json_compatible(result)
