# -*- coding: utf-8 -*-
from plone.app.event.base import default_timezone
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from Products.CMFPlone.interfaces import IImagingSchema
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.utils import getSiteLogo
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Site:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {"site": {"@id": f"{self.context.absolute_url()}/@site"}}
        if not expand:
            return result

        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
        image_settings = registry.forInterface(
            IImagingSchema, prefix="plone", check=False
        )
        result["site"].update(
            {
                "plone.site_title": portal_state.portal_title(),
                "plone.site_logo": site_settings.site_logo and getSiteLogo() or None,
                "plone.robots_txt": site_settings.robots_txt,
                "plone.allowed_sizes": image_settings.allowed_sizes,
                "plone.site_timezone": default_timezone(self.context),
            }
        )

        return result


class SiteGet(Service):
    def reply(self):
        site = Site(self.context, self.request)
        return site(expand=True)["site"]
