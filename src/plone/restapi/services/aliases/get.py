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
        self.request.response.setStatus(201)
        return [{"path": alias} for alias in aliases]

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

        self.request.form["b_start"] = "0"
        self.request.form["b_size"] = "1000000"
        self.request.__annotations__.pop("plone.memoize")

        newbatch = RedirectsControlPanel(self.context, self.request).redirects()
        items_total = len([item for item in newbatch])
        return redirects, items_total

    def __call__(self, expand=False):
        result = {"aliases": {"@id": f"{self.context.absolute_url()}/@aliases"}}
        if not expand:
            return result

        if IPloneSiteRoot.providedBy(self.context):
            items, items_total = self.reply_root()
            result["aliases"]["items"] = items
            result["aliases"]["items_total"] = items_total
        else:
            result["aliases"]["items"] = self.reply_item()
            result["aliases"]["items_total"] = len(result["aliases"]["items"])

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
