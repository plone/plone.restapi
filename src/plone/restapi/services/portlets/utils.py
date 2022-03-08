# -*- coding: utf-8 -*-
from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.portlets.interfaces import IPortletManager
from zope.component import getUtilitiesFor
from zope.component import getUtility


def get_portlet_types():
    return getUtilitiesFor(IPortletTypeInterface)


def get_portletmanagers():
    return getUtilitiesFor(IPortletManager)


def manager_by_name(context, name):
    return getUtility(IPortletManager,
                      name=name,
                      context=context)
