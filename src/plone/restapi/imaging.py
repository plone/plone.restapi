# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import IPropertiesTool
from zope.component import getUtility


try:
    from Products.CMFPlone.factory import _IMREALLYPLONE5  # noqa
except ImportError:
    PLONE_5 = False  # pragma: no cover
else:
    PLONE_5 = True  # pragma: no cover


def get_scales(context):
    absolute_url = context.absolute_url()
    scales = {name: '{0}/@@images/image/{1}'.format(absolute_url, name)
              for name in get_scale_names()}
    return scales


def get_scale_names():
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
