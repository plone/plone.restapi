# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import IPropertiesTool
from zope.component import getUtility


try:
    from Products.CMFPlone.factory import _IMREALLYPLONE5  # noqa
except ImportError:
    PLONE_5 = False  # pragma: no cover
else:
    PLONE_5 = True  # pragma: no cover


def get_scales(context, field, width, height):
    """Get a dictionary of available scales for a particular image field,
    with the actual dimensions (aspect ratio of the original image).
    """
    scales = {}
    absolute_url = context.absolute_url()

    for name, scale_width, scale_height in get_scale_infos():
        bbox = scale_width, scale_height
        actual_width, actual_height = get_actual_scale((width, height), bbox)
        url = u'{}/@@images/{}/{}'.format(absolute_url, field.__name__, name)

        scales[name] = {
            u'download': url,
            u'width': actual_width,
            u'height': actual_height}

    return scales


def get_actual_scale(dimensions, bbox):
    """Given dimensions of an original image, and a bounding box of a scale,
    calculates what actual dimensions that scaled image would have,
    maintaining aspect ratio.

    This is supposed to emulate / predict the behavior of Plone's
    ImageScaling implementations.
    """
    width, height = map(float, dimensions)
    max_width, max_height = map(float, bbox)
    resize_ratio = min(max_width / width, max_height / height)

    # Plone doesn't upscale images for the default named scales - limit
    # to actual image dimensions
    resize_ratio = min(resize_ratio, 1.0)

    scaled_dimensions = int(width * resize_ratio), int(height * resize_ratio)

    # Don't produce zero pixel lengths
    scaled_dimensions = tuple(max(1, dim) for dim in scaled_dimensions)
    return scaled_dimensions


def get_scale_infos():
    """Returns a list of (name, width, height) 3-tuples of the
    available image scales.
    """
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

    def split_scale_info(allowed_size):
        name, dims = allowed_size.split(' ')
        width, height = map(int, dims.split(':'))
        return name, width, height

    return [split_scale_info(size) for size in allowed_sizes]
