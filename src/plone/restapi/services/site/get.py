# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface

try:
    from Products.CMFPlone.utils import getSiteLogo
except ImportError:
    getSiteLogo = None
try:
    from Products.CMFPlone.interfaces import IImagingSchema
except ImportError:
    IImagingSchema = None
try:
    from Products.CMFPlone.interfaces import ISiteSchema
except ImportError:
    ISiteSchema = None


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Site:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {"site": {"@id": "{}/@site".format(self.context.absolute_url())}}
        if not expand:
            return result

        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        registry = getUtility(IRegistry)

        if ISiteSchema is not None:
            site_settings = registry.forInterface(
                ISiteSchema, prefix="plone", check=False
            )
            result["site"].update(
                {
                    "plone.site_logo": site_settings.site_logo
                    and getSiteLogo()
                    or None,
                    "plone.robots_txt": site_settings.robots_txt,
                }
            )

        if IImagingSchema is not None:
            image_settings = registry.forInterface(
                IImagingSchema, prefix="plone", check=False
            )
            result["site"].update(
                {
                    "plone.allowed_sizes": image_settings.allowed_sizes,
                }
            )

        result["site"].update(
            {
                "plone.site_title": portal_state.portal_title(),
            }
        )

        return result


class SiteGet(Service):
    def reply(self):
        site = Site(self.context, self.request)
        return site(expand=True)["site"]
