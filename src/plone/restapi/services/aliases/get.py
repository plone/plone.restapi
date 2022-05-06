from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.component import getUtility
from plone.app.redirector.interfaces import IRedirectionStorage
from zope.component.hooks import getSite
from Products.CMFPlone.controlpanel.browser.redirects import RedirectsControlPanel
from plone.restapi.serializer.converters import datetimelike_to_iso


@implementer(IPublishTraverse)
class AliasesGet(Service):
    def reply(self):
        storage = getUtility(IRedirectionStorage)
        context_path = "/".join(self.context.getPhysicalPath())
        redirects = storage.redirects(context_path)
        aliases = [deroot_path(alias) for alias in redirects]
        self.request.response.setStatus(201)
        response = {
            "@id": self.request.URL,
            "items": [{"path": alias} for alias in aliases],
        }
        return response


@implementer(IPublishTraverse)
class AliasesRootGet(Service):
    def reply(self):
        """
        redirect-to - target
        path        - path
        redirect    - full path with root
        """
        batch = RedirectsControlPanel(self.context, self.request).redirects()
        redirects = [entry for entry in batch]

        for redirect in redirects:
            del redirect["redirect"]
            redirect["datetime"] = datetimelike_to_iso(redirect["datetime"])
        self.request.response.setStatus(201)

        response = {"@id": self.request.URL, "items": redirects}
        return response


def deroot_path(path):
    """Remove the portal root from alias"""
    portal = getSite()
    root_path = "/".join(portal.getPhysicalPath())
    return path.replace(root_path, "", 1)
