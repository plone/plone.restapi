# -*- coding: utf-8 -*-

from .interfaces import ISlotSettings
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.z3cform import layout
from z3c.form import form
from zope.component import adapter
from zope.interface import Interface


class SlotsControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = ISlotSettings


SlotsControlPanelView = layout.wrap_form(SlotsControlPanelForm, ControlPanelFormWrapper)
SlotsControlPanelView.label = u"Slots"


@adapter(Interface, Interface)
class SlotsControlpanel(RegistryConfigletPanel):
    schema = ISlotSettings

    configlet_id = "SlotSettings"
    configlet_category_id = "plone-content"
