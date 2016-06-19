# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from plone.restapi.services import Service
from zope.component import getUtility
from zope.interface import alsoProvides

import json
import plone.protect.interfaces


class RegistryUpdate(Service):

    def reply(self):
        records_to_update = json.loads(self.request.get('BODY', '{}'))
        registry = getUtility(IRegistry)

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        for key, value in records_to_update.items():
            if key not in registry:
                raise NotImplementedError(
                    "This endpoint is only intended to update existing "
                    "records! Couldn't find key %r" % key)
            registry[key] = value
        self.request.response.setStatus(204)
        return None
