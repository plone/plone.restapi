# -*- coding: utf-8 -*-
from plone.restapi.imaging import get_original_image_url
from plone.restapi.imaging import get_scales
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces.field import IField
from Products.Archetypes.interfaces.field import IFileField
from Products.Archetypes.interfaces.field import IImageField
from Products.Archetypes.interfaces.field import IReferenceField
from Products.Archetypes.interfaces.field import ITextField
from Products.CMFCore.utils import getToolByName
from six.moves import map
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import pkg_resources


# When we have plone.app.collection, we need a serializer for IQueryField.
# On Plone 5 it comes from p.a.collection.
# On Plone 4 we also have p.a.collection, but the field is in archetypes.querywidget.
try:
    pkg_resources.get_distribution("plone.app.collection")
except pkg_resources.DistributionNotFound:
    IQueryField = None
else:
    try:
        from plone.app.collection.field import IQueryField
    except ImportError:
        from archetypes.querywidget.interfaces import IQueryField

try:
    pkg_resources.get_distribution("plone.app.blob")
except pkg_resources.DistributionNotFound:
    HAS_BLOB = False
else:
    HAS_BLOB = True
    from plone.app.blob.interfaces import IBlobField
    from plone.app.blob.interfaces import IBlobImageField


@adapter(IField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class DefaultFieldSerializer(object):
    def __init__(self, field, context, request):
        self.context = context
        self.request = request
        self.field = field

    def __call__(self):
        accessor = self.field.getAccessor(self.context)
        return json_compatible(accessor())


@adapter(IFileField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class FileFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        url = "/".join(
            (self.context.absolute_url(), "@@download", self.field.getName())
        )
        result = {
            "filename": self.field.getFilename(self.context),
            "content-type": self.field.getContentType(self.context),
            "size": self.field.get_size(self.context),
            "download": url,
        }
        return json_compatible(result)


@adapter(ITextField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class TextFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        mimetypes_registry = getToolByName(self.context, "mimetypes_registry")
        data = super(TextFieldSerializer, self).__call__()
        return {
            "content-type": json_compatible(mimetypes_registry(data)[2].normalized()),
            "data": data,
        }


@adapter(IImageField, IBaseObject, Interface)
@implementer(IFieldSerializer)
class ImageFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        image = self.field.get(self.context)
        if not image:
            return None

        width, height = image.width, image.height
        url = get_original_image_url(self.context, self.field.__name__, width, height)

        scales = get_scales(self.context, self.field, width, height)
        result = {
            "filename": self.field.getFilename(self.context),
            "content-type": self.field.get(self.context).getContentType(),
            "size": self.field.get(self.context).get_size(),
            "download": url,
            "width": width,
            "height": height,
            "scales": scales,
        }
        return json_compatible(result)


if HAS_BLOB:

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


if IQueryField is not None:

    @adapter(IQueryField, IBaseObject, Interface)
    @implementer(IFieldSerializer)
    class QueryFieldSerializer(DefaultFieldSerializer):
        def __call__(self):
            raw_value = self.field.getRaw(self.context)
            return json_compatible(list(map(dict, raw_value)))
