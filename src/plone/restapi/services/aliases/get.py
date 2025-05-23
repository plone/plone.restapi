from plone.app.redirector.interfaces import IRedirectionStorage
from plone.restapi.bbb import IPloneSiteRoot
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import datetimelike_to_iso
from plone.restapi.services import Service
from Products.CMFPlone.controlpanel.browser.redirects import RedirectsControlPanel
from zope.component import adapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface

import json


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
        self.request.response.setStatus(200)
        self.request.response.setHeader("Content-Type", "application/json")
        return [{"path": alias} for alias in aliases], len(aliases)

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
        self.request.response.setStatus(200)

        self.request.form["b_start"] = "0"
        self.request.form["b_size"] = "1000000"
        self.request.__annotations__.pop("plone.memoize")

        newbatch = RedirectsControlPanel(self.context, self.request).redirects()
        items_total = len([item for item in newbatch])
        self.request.response.setHeader("Content-Type", "application/json")

        return redirects, items_total

    def reply_root_csv(self):
        batch = RedirectsControlPanel(self.context, self.request).redirects()
        redirects = [entry for entry in batch]

        for redirect in redirects:
            del redirect["redirect"]
            redirect["datetime"] = datetimelike_to_iso(redirect["datetime"])
        self.request.response.setStatus(200)

        self.request.form["b_start"] = "0"
        self.request.form["b_size"] = "1000000"
        self.request.__annotations__.pop("plone.memoize")

        filestream = RedirectsControlPanel(self.context, self.request).download()
        content = filestream.read()
        filestream.close()

        self.request.response.setHeader("Content-Type", "text/csv")
        self.request.response.setHeader(
            "Content-Disposition", "attachment; filename=redirects.csv"
        )
        self.request.response.setHeader("Content-Length", str(len(content)))
        return content

    def __call__(self, expand=False):
        result = {"aliases": {"@id": f"{self.context.absolute_url()}/@aliases"}}
        if not expand:
            return result
        if IPloneSiteRoot.providedBy(self.context):
            if self.request.getHeader("Accept") == "text/csv":
                result["aliases"]["items"] = self.reply_root_csv()
                return result
            else:
                items, items_total = self.reply_root()
        else:
            items, items_total = self.reply_item()
        result["aliases"]["items"] = items
        result["aliases"]["items_total"] = items_total
        return result


_no_content_marker = object()


class AliasesGet(Service):
    """Get aliases"""

    def reply(self):
        aliases = Aliases(self.context, self.request)
        return aliases(expand=True)["aliases"]

    def render(self):
        self.check_permission()
        content = self.reply()
        if self.request.getHeader("Accept") == "text/csv":
            return content["items"]
        if content is not _no_content_marker:
            return json.dumps(
                content, indent=2, sort_keys=True, separators=(", ", ": ")
            )


def deroot_path(path):
    """Remove the portal root from alias"""
    portal = getSite()
    root_path = "/".join(portal.getPhysicalPath())
    if not path.startswith("/"):
        path = "/%s" % path
    return path.replace(root_path, "", 1)
