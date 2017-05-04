# -*- coding: utf-8 -*-
from zope.interface import implementer, Interface, Attribute
from zope.component import adapter
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.interfaces.controlpanel import IDateAndTimeSchema
from Products.CMFPlone.interfaces.controlpanel import IEditingSchema
from Products.CMFPlone.interfaces.controlpanel import ILanguageSchema
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.interfaces.controlpanel import INavigationSchema
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.CMFPlone.interfaces.controlpanel import ISearchSchema
from Products.CMFPlone.interfaces.controlpanel import ISocialMediaSchema
from Products.CMFPlone.interfaces.controlpanel import IImagingSchema
from Products.CMFPlone.interfaces.controlpanel import IMarkupSchema
from Products.CMFPlone.interfaces.controlpanel import ISecuritySchema


class IControlpanel(Interface):
    __name__ = Attribute('Name of the controlpanel in the URL')
    title = Attribute('Title of this controlpanel')
    group = Attribute('Group name of this controlpanel')
    schema = Attribute('Registry schema of this controlpanel')

    configlet_id = Attribute('Id the configlet, ie MailHost')
    configlet_category_id = Attribute('Category of the configlet, ie plone-general')  # noqa


@implementer(IControlpanel)
class RegistryConfigletPanel(object):
    configlet = None
    configlet_id = None
    configlet_category_id = None
    schema = None

    schema_prefix = 'plone'

    def _get_configlet(self):
        configlet_data = self.portal_cp.enumConfiglets(
            self.configlet_category_id
        )
        for action in configlet_data:
            if action['id'] == self.configlet_id:
                return action

    def _get_group_title(self):
        groups = [
            g for g in self.portal_cp.getGroups()
            if g['id'] == self.configlet['category']
        ]
        return [g['title'] for g in groups][0]

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.portal_cp = getToolByName(self.context, 'portal_controlpanel')

        self.configlet = self._get_configlet()
        if self.configlet:
            self.title = self.configlet['title']
            self.group = self._get_group_title()


# General

@adapter(Interface, Interface)
class DateTimeControlpanel(RegistryConfigletPanel):
    schema = IDateAndTimeSchema
    configlet_id = 'DateAndTime'
    configlet_category_id = 'plone-general'


@adapter(Interface, Interface)
class LanguageControlpanel(RegistryConfigletPanel):
    schema = ILanguageSchema
    configlet_id = 'LanguageSettings'
    configlet_category_id = 'plone-general'


@adapter(Interface, Interface)
class MailControlpanel(RegistryConfigletPanel):
    schema = IMailSchema
    configlet_id = 'MailHost'
    configlet_category_id = 'plone-general'


@adapter(Interface, Interface)
class NavigationControlpanel(RegistryConfigletPanel):
    schema = INavigationSchema
    configlet_id = 'NavigationSettings'
    configlet_category_id = 'plone-general'


@adapter(Interface, Interface)
class SiteControlpanel(RegistryConfigletPanel):
    schema = ISiteSchema
    configlet_id = 'PloneReconfig'
    configlet_category_id = 'plone-general'


@adapter(Interface, Interface)
class SearchControlpanel(RegistryConfigletPanel):
    schema = ISearchSchema
    configlet_id = 'SearchSettings'
    configlet_category_id = 'plone-general'


@adapter(Interface, Interface)
class SocialMediaControlpanel(RegistryConfigletPanel):
    schema = ISocialMediaSchema
    configlet_id = 'socialmedia'
    configlet_category_id = 'plone-general'


# Content

@adapter(Interface, Interface)
class EditingControlpanel(RegistryConfigletPanel):
    schema = IEditingSchema
    configlet_id = 'EditingSettings'
    configlet_category_id = 'plone-content'


@adapter(Interface, Interface)
class ImagingControlpanel(RegistryConfigletPanel):
    schema = IImagingSchema
    configlet_id = 'ImagingSettings'
    configlet_category_id = 'plone-content'


@adapter(Interface, Interface)
class MarkupControlpanel(RegistryConfigletPanel):
    schema = IMarkupSchema
    configlet_id = 'MarkupSettings'
    configlet_category_id = 'plone-content'


# Security

@adapter(Interface, Interface)
class SecurityControlpanel(RegistryConfigletPanel):
    schema = ISecuritySchema
    configlet_id = 'SecuritySettings'
    configlet_category_id = 'plone-security'
