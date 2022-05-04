from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.component import getUtility
from zope.component.hooks import getSite
from plone.app.redirector.interfaces import IRedirectionStorage
import json


@implementer(IPublishTraverse)
class AliasesGet(Service):
    def reply(self):
        storage = getUtility(IRedirectionStorage)
        context_path = "/".join(self.context.getPhysicalPath())
        redirects = storage.redirects(context_path)
        return {"aliases": json.dumps(redirects)}
