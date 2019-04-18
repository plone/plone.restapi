# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager

from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.restapi.services.addons.addons import Addons
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import AddPortalMember
from Products.CMFCore.permissions import SetOwnPassword
from zope.component import getAdapter
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

import plone

from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFQuickInstallerTool.interfaces import INonInstallable as \
    QINonInstallable
from Products.Five.browser import BrowserView
from Products.GenericSetup import EXTENSION
from Products.GenericSetup.tool import UNKNOWN
from Products.statusmessages.interfaces import IStatusMessage
from plone.memoize import view
from zope.component import getAllUtilitiesRegisteredFor
import logging
import pkg_resources
import transaction
import warnings

logger = logging.getLogger('Plone')


class AddonsPost(Service):
    """Performs install/upgrade/uninstall functions on an addon."""

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(AddonsPost, self).__init__(context, request)
        self.params = []
        self.errors = {}
        self.addons = Addons(context, request)
    
    def publishTraverse(self, request, name):
        # Consume any path segments after /@addons as parameters
        self.params.append(name)
        return self

    def reply(self):
        addon, action = self.params

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        if action == 'install':
            result = self.addons.install_product(addon)
        elif action == 'uninstall':
            result = self.addons.uninstall_product(addon)
        elif action == 'upgrade':
            result = self.addons.upgrade_product(addon)
        else:
            raise Exception("Unknown action {}".format(action))

        prefer = self.request.getHeader('Prefer')
        if prefer == 'return=representation':
            control_panel = getMultiAdapter((self.context, self.request),
                                            name='prefs_install_products_form')
            all_addons = control_panel.get_addons()

            result = {
                'items': {
                    '@id': '{}/@addons'.format(self.context.absolute_url()),
                },
            }
            addons_data = []
            for a in all_addons.itervalues():
                addons_data.append(self.addons.serializeAddon(a))
            result['items'] = addons_data

            self.request.response.setStatus(200)
            return result
        else:
            self.request.response.setStatus(204)
            return None
