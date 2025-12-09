from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.restapi.batching import HypermediaBatch
from plone.restapi.bbb import IPloneSiteRoot
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import datetimelike_to_iso
from plone.restapi.services import Service
from plone.restapi.utils import deroot_path
from plone.restapi.utils import is_falsy
from plone.restapi.utils import is_truthy
from Products.CMFPlone.controlpanel.browser.redirects import RedirectsControlPanel
from zExceptions import BadRequest
from zExceptions import HTTPNotAcceptable as NotAcceptable
from zope.component import adapter
from zope.component import getUtility
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

    def reply(self, query, manual, start, end):
        storage = getUtility(IRedirectionStorage)
        portal_path = "/".join(self.context.getPhysicalPath()[:2])
        context_path = "/".join(self.context.getPhysicalPath())

        if not IPloneSiteRoot.providedBy(self.context):
            tree = OOBTree()
            rds = storage.redirects(context_path)
            for rd in rds:
                rd_full = storage.get_full(rd)
                tree[rd] = rd_full
            storage = tree
        else:
            storage = storage._paths

        if query and query.startswith("/"):
            min_k = f"{portal_path}/{query.strip('/')}"
            max_k = min_k[:-1] + chr(ord(min_k[-1]) + 1)
            redirects = storage.items(min=min_k, max=max_k, excludemax=True)
        elif query:
            redirects = [path for path in storage.items() if query in path]
        else:
            redirects = storage.items()

        aliases = []
        for path, info in redirects:
            if manual and info[2] != manual:
                continue
            if start and info[1]:
                if info[1] < start:
                    continue
            if end and info[1]:
                if info[1] >= end:
                    continue

            redirect = {
                "path": deroot_path(path),
                "redirect-to": deroot_path(info[0]),
                "datetime": datetimelike_to_iso(info[1]),
                "manual": info[2],
            }
            aliases.append(redirect)

        batch = HypermediaBatch(self.request, aliases)

        self.request.response.setStatus(200)
        self.request.response.setHeader("Content-Type", "application/json")
        return [i for i in batch], batch.items_total, batch.links

    def reply_root_csv(self):
        if not IPloneSiteRoot.providedBy(self.context):
            raise NotAcceptable("CSV reply is only available from site root.")

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
        data = self.request.form

        query = data.get("query", data.get("q", None))
        manual = data.get("manual", None)
        start = data.get("start", None)
        end = data.get("end", None)

        if query and not isinstance(query, str):
            raise BadRequest('Parameter "query" must be a string.')

        if manual and not (is_truthy(manual) or is_falsy(manual)):
            raise BadRequest('Parameter "manual" must be a boolean.')

        for value in (start, end):
            if value:
                try:
                    value = DateTime(value)
                except Exception as e:
                    raise BadRequest(str(e))

        result = {"aliases": {"@id": f"{self.context.absolute_url()}/@aliases"}}
        if not expand:
            return result
        if self.request.getHeader("Accept") == "text/csv":
            result["aliases"]["items"] = self.reply_root_csv()
            return result
        else:
            items, items_total, batching = self.reply(query, manual, start, end)

        result["aliases"]["items"] = items
        result["aliases"]["items_total"] = items_total
        if batching:
            result["aliases"]["links"] = batching

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
