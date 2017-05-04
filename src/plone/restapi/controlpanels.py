# -*- coding: utf-8 -*-
from zope.interface import implementer, Interface, Attribute
from zope.component import adapter
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.interfaces import IEditingSchema
from Products.CMFPlone.interfaces.controlpanel import IMailSchema


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


@implementer(IControlpanel)
@adapter(Interface, Interface)
class EditingControlpanel(RegistryConfigletPanel):
    registry_schema = IEditingSchema
    configlet_id = 'EditingSettings'
    configlet_category_id = 'plone-content'


@implementer(IControlpanel)
@adapter(Interface, Interface)
class MailControlpanel(RegistryConfigletPanel):
    registry_schema = IMailSchema
    configlet_id = 'MailHost'
    configlet_category_id = 'plone-general'
