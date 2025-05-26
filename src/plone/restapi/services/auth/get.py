from plone.restapi.interfaces import ILoginProviders
from plone.restapi.services import Service
from zope.component import getAdapters


class Login(Service):
    def reply(self):
        adapters = getAdapters((self.context,), ILoginProviders)
        external_providers = []
        for name, adapter in adapters:
            external_providers.extend(adapter.get_providers())

        return {"options": external_providers}
