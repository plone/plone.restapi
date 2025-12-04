from BTrees.OOBTree import OOBTree
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.restapi.batching import HypermediaBatch
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

    def reply(self):
        storage = getUtility(IRedirectionStorage)
        form = self.request.form
        portal_path = "/".join(self.context.getPhysicalPath()[:2])
        context_path = "/".join(self.context.getPhysicalPath())

        if not IPloneSiteRoot.providedBy(self.context):
            storage = OOBTree(
                (key, value)
                for key, value in storage._paths.items()
                if value[0] == context_path
            )
        else:
            storage = storage._paths

        query = form.get("q") or form.get("query")
        if query and query.startswith("/"):
            min_k = f"{portal_path}/{query.strip('/')}"
            max_k = min_k[:-1] + chr(ord(min_k[-1]) + 1)
            redirects = storage.items(min=min_k, max=max_k, excludemax=True)
        elif query:
            redirects = [path for path in storage.items() if query in path]
        else:
            redirects = storage.items()

        aliases = []
        for redirect in redirects:
            info = storage.get_full(redirect)
            if form.get("manual") and info[2] != form["manual"]:
                continue
            if form.get("start") and info[1]:
                if info[1] < form["start"]:
                    continue
            if form.get("end") and info[1]:
                if info[1] >= form["end"]:
                    continue

            redirect = {
                "path": redirect,
                "redirect-to": info[0],
                "datetime": datetimelike_to_iso(info[1]),
                "manual": info[2],
            }
            aliases.append(redirect)

        batch = HypermediaBatch(self.request, aliases)

        breakpoint()
        self.request.response.setStatus(200)
        self.request.response.setHeader("Content-Type", "application/json")
        return batch, batch.items_total, batch.links

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
        if self.request.getHeader("Accept") == "text/csv":
            result["aliases"]["items"] = self.reply_root_csv()
            return result
        else:
            items, items_total, batching = self.reply()
        result["aliases"]["items"] = items
        result["aliases"]["items_total"] = items_total
        result["aliases"]["batching"] = batching
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
