from plone.app.event.base import FALLBACK_TIMEZONE
from plone.app.event.base import replacement_zones
from plone.event.utils import default_timezone as fallback_default_timezone
from plone.event.utils import validated_timezone
from plone.i18n.interfaces import ILanguageSchema
from plone.registry.interfaces import IRegistry
from plone.restapi import HAS_MULTILINGUAL
from plone.restapi.bbb import IImagingSchema
from plone.restapi.bbb import ISiteSchema
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISiteEndpointExpander
from plone.restapi.services import Service
from Products.CMFPlone.controlpanel.browser.redirects import RedirectionSet
from Products.CMFPlone.utils import getSiteLogo
from zope.component import adapter
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface


if HAS_MULTILINGUAL:
    from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled


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
        language_settings = registry.forInterface(
            ILanguageSchema, prefix="plone", check=False
        )
        result["site"].update(
            {
                "plone.site_title": portal_state.portal_title(),
                "plone.site_logo": site_settings.site_logo and getSiteLogo() or None,
                "plone.robots_txt": site_settings.robots_txt,
                "plone.allowed_sizes": image_settings.allowed_sizes,
                "plone.default_language": language_settings.default_language,
                "plone.available_languages": language_settings.available_languages,
                "plone.portal_timezone": self.plone_timezone(),
                "features": self.features(),
            }
        )

        expanders = getAdapters(
            (self.context, self.request), provided=ISiteEndpointExpander
        )
        for name, expander in expanders:
            expander(result["site"])

        return result

    def plone_timezone(self):
        """Returns the portal timezone"""

        reg_key = "plone.portal_timezone"
        registry = getUtility(IRegistry)
        portal_timezone = registry.get(reg_key, None)

        # fallback to what plone.event is doing
        if not portal_timezone:
            portal_timezone = fallback_default_timezone()

        # Change any ambiguous timezone abbreviations to their most common
        # non-ambigious timezone name.
        if portal_timezone in replacement_zones.keys():
            portal_timezone = replacement_zones[portal_timezone]
        portal_timezone = validated_timezone(portal_timezone, FALLBACK_TIMEZONE)

        return portal_timezone

    def features(self):
        """Indicates which features are supported by this site.

        This can be used by a client to check for version-dependent features.
        """
        result = {
            "filter_aliases_by_date": hasattr(
                RedirectionSet, "supports_date_range_filtering"
            ),
            "multilingual": HAS_MULTILINGUAL
            and IPloneAppMultilingualInstalled.providedBy(self.request),
        }
        return result


class SiteGet(Service):
    def reply(self):
        site = Site(self.context, self.request)
        return site(expand=True)["site"]
