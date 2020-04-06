# -*- coding: utf-8 -*-
from zope.interface import Attribute
from zope.interface import Interface


class IControlpanel(Interface):
    __name__ = Attribute("Name of the controlpanel in the URL")
    title = Attribute("Title of this controlpanel")
    group = Attribute("Group name of this controlpanel")
    schema = Attribute("Registry schema of this controlpanel")

    configlet_id = Attribute("Id the configlet, ie MailHost")
    configlet_category_id = Attribute(
        "Category of the configlet, ie plone-general"
    )  # noqa


class IDexterityTypesControlpanel(IControlpanel):
    """ Dexterity Types Control panel """
