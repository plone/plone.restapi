# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from zope.component import getAdapters
from plone.restapi.interfaces import IExternalLoginProviders


class Login(Service):
    def reply(self):
        adapters = getAdapters(self.context, IExternalLoginProviders)
        external_providers = []
        for adapter in adapters:
            external_providers.extend(
                adapter.get_providers()
            )

        return {'options': external_providers}