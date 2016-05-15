# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from plone.rest import Service
from zope.component import getUtility

import json


class RegistryUpdate(Service):

    def render(self):
        records_to_update = json.loads(self.request.get('BODY', '{}'))
        registry = getUtility(IRegistry)

        for key, value in records_to_update.items():
            if key not in registry:
                raise Exception(
                    "This endpoint is only intended to update existing "
                    "records! Couldn't find key %r" % key)
            registry[key] = value
        self.request.response.setStatus(204)
        return None
