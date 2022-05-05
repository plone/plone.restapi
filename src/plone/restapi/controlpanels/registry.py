from plone.base.interfaces.controlpanel import IDateAndTimeSchema
from plone.base.interfaces.controlpanel import IEditingSchema
from plone.base.interfaces.controlpanel import IImagingSchema
from plone.base.interfaces.controlpanel import IMailSchema
from plone.base.interfaces.controlpanel import IMarkupSchema
from plone.base.interfaces.controlpanel import INavigationSchema
from plone.base.interfaces.controlpanel import ISearchSchema
from plone.base.interfaces.controlpanel import ISecuritySchema
from plone.base.interfaces.controlpanel import ISiteSchema
from plone.base.interfaces.controlpanel import ISocialMediaSchema
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import Interface


try:
    from plone.i18n.interfaces import ILanguageSchema
except ImportError:  # pragma: no cover
    from plone.base.interfaces.controlpanel import ILanguageSchema


# General
@adapter(Interface, Interface)
class DateTimeControlpanel(RegistryConfigletPanel):
    schema = IDateAndTimeSchema
    configlet_id = "DateAndTime"
    configlet_category_id = "plone-general"


@adapter(Interface, Interface)
class LanguageControlpanel(RegistryConfigletPanel):
    schema = ILanguageSchema
    configlet_id = "LanguageSettings"
    configlet_category_id = "plone-general"


@adapter(Interface, Interface)
class MailControlpanel(RegistryConfigletPanel):
    schema = IMailSchema
    configlet_id = "MailHost"
    configlet_category_id = "plone-general"


@adapter(Interface, Interface)
class NavigationControlpanel(RegistryConfigletPanel):
    schema = INavigationSchema
    configlet_id = "NavigationSettings"
    configlet_category_id = "plone-general"


@adapter(Interface, Interface)
class SiteControlpanel(RegistryConfigletPanel):
    schema = ISiteSchema
    configlet_id = "PloneReconfig"
    configlet_category_id = "plone-general"


@adapter(Interface, Interface)
class SearchControlpanel(RegistryConfigletPanel):
    schema = ISearchSchema
    configlet_id = "SearchSettings"
    configlet_category_id = "plone-general"


@adapter(Interface, Interface)
class SocialMediaControlpanel(RegistryConfigletPanel):
    schema = ISocialMediaSchema
    configlet_id = "socialmedia"
    configlet_category_id = "plone-general"


# Content


@adapter(Interface, Interface)
class EditingControlpanel(RegistryConfigletPanel):
    schema = IEditingSchema
    configlet_id = "EditingSettings"
    configlet_category_id = "plone-content"


@adapter(Interface, Interface)
class ImagingControlpanel(RegistryConfigletPanel):
    schema = IImagingSchema
    configlet_id = "ImagingSettings"
    configlet_category_id = "plone-content"


@adapter(Interface, Interface)
class MarkupControlpanel(RegistryConfigletPanel):
    schema = IMarkupSchema
    configlet_id = "MarkupSettings"
    configlet_category_id = "plone-content"


# Security


@adapter(Interface, Interface)
class SecurityControlpanel(RegistryConfigletPanel):
    schema = ISecuritySchema
    configlet_id = "SecuritySettings"
    configlet_category_id = "plone-security"
