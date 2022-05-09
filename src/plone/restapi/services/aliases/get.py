from plone.app.redirector.interfaces import IRedirectionStorage
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import datetimelike_to_iso
from plone.restapi.services import Service
from Products.CMFPlone.controlpanel.browser.redirects import RedirectsControlPanel
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Aliases:
    """@aliases"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def reply_item(self):
        storage = getUtility(IRedirectionStorage)
        context_path = "/".join(self.context.getPhysicalPath())
        redirects = storage.redirects(context_path)
        aliases = [deroot_path(alias) for alias in redirects]
        redirect_to = deroot_path(self.context.absolute_url(1))
        self.request.response.setStatus(201)
        return [{"path": alias, "redirect-to": redirect_to} for alias in aliases]

    def reply_root(self):
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

        return redirects

    def __call__(self, expand=False):
        result = {"aliases": {"@id": f"{self.context.absolute_url()}/@aliases"}}
        if not expand:
            return result

        if IPloneSiteRoot.providedBy(self.context):
            result["aliases"]["items"] = self.reply_root()
        else:
            result["aliases"]["items"] = self.reply_item()
        return result


class AliasesGet(Service):
    """Get aliases"""

    def reply(self):
        aliases = Aliases(self.context, self.request)
        return aliases(expand=True)["aliases"]


def deroot_path(path):
    """Remove the portal root from alias"""
    portal = getSite()
    root_path = "/".join(portal.getPhysicalPath())
    if not path.startswith("/"):
        path = "/%s" % path
    return path.replace(root_path, "", 1)
