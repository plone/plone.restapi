from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.component import getUtility
from plone.app.redirector.interfaces import IRedirectionStorage
from zope.component.hooks import getSite


@implementer(IPublishTraverse)
class AliasesGet(Service):
    def reply(self):
        storage = getUtility(IRedirectionStorage)
        context_path = "/".join(self.context.getPhysicalPath())
        redirects = storage.redirects(context_path)
        aliases = [deroot_path(alias) for alias in redirects]
        self.request.response.setStatus(201)
        return {"aliases": aliases}


def deroot_path(path):
    """ Remove the portal root from alias """
    portal = getSite()
    root_path = "/".join(portal.getPhysicalPath())
    return path.replace(root_path, "", 1)
