from Acquisition import aq_parent
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware
from zope.component import getMultiAdapter
import re

PATH_RE = re.compile(r"^(.*?)((?=/@@|#).*)?$")


def path2uid(context, link):
    # unrestrictedTraverse requires a string on py3. see:
    # https://github.com/zopefoundation/Zope/issues/674
    if not link:
        return ""
    portal = getMultiAdapter(
        (context, context.REQUEST), name="plone_portal_state"
    ).portal()
    portal_url = portal.portal_url()
    portal_path = "/".join(portal.getPhysicalPath())
    path = link
    context_url = context.absolute_url()
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
