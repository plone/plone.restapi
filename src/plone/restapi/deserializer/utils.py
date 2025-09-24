from Acquisition import aq_parent
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getUtility
from zope.component.hooks import getSite

import re


PATH_RE = re.compile(r"^(.*?)((?=/@@|#).*)?$")


def get_portal():
    closest_site = getSite()
    if closest_site is not None:
        for potential_portal in closest_site.aq_chain:
            if ISiteRoot.providedBy(potential_portal):
                return potential_portal
    raise Exception("Plone site root not found")


def path2uid(context, link):
    if not link:
        return ""
    portal = get_portal()
    portal_url = portal.portal_url()
    portal_path = "/".join(portal.getPhysicalPath())
    path = link
    try:
        context_url = context.absolute_url()
    except AttributeError:
        context_url = portal_url
    relative_up = len(context_url.split("/")) - len(portal_url.split("/"))
    if path.startswith(portal_url):
        path = path[len(portal_url) + 1 :]
    if not path.startswith(portal_path):
        path = "{portal_path}/{path}".format(
            portal_path=portal_path, path=path.lstrip("/")
        )

    # handle edge cases with suffixes like /@@download/file or a fragment
    suffix = ""
    match = PATH_RE.match(path)
    if match is not None:
        path = match.group(1).rstrip("/")
        suffix = match.group(2) or ""

    obj = portal.unrestrictedTraverse(path, None)
    if obj is None:
        # last try: maybe the object or some parent has been renamed.
        # if yes, there should be a reference into redirection storage
        storage = getUtility(IRedirectionStorage)
        alias_path = storage.get(path)
        if alias_path:
            path = alias_path
            obj = portal.unrestrictedTraverse(path, None)
    if obj is None or obj == portal:
        return link
    segments = path.split("/")
    while not IUUIDAware.providedBy(obj):
        obj = aq_parent(obj)
        if obj is None:
            break
        suffix = "/" + segments.pop() + suffix
    # check if obj is wrong because of acquisition
    if not obj or "/".join(obj.getPhysicalPath()) != "/".join(segments):
        return link
    href = relative_up * "../" + "resolveuid/" + IUUID(obj)
    if suffix:
        href += suffix
    return href
