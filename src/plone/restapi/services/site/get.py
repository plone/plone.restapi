# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from plone.restapi.services import Service
from Products.CMFPlone.interfaces import IImagingSchema
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.utils import getSiteLogo
from zope.component import getMultiAdapter
from zope.component import getUtility


class SiteGet(Service):
    def reply(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False
        )
        image_settings = registry.forInterface(
            IImagingSchema, prefix="plone", check=False
        )
        return {
            "title": portal_state.portal_title(),
            "logo": site_settings.site_logo and getSiteLogo() or None,
            "robots_txt": site_settings.robots_txt,
            "imaging_allowed_sizes": image_settings.allowed_sizes,
        }
