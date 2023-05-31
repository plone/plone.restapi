from Acquisition import aq_parent
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware
from zope.component import getMultiAdapter

import re


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
    suffix = ""

    # handle edge-case when we have path with /@@download/file for example
    suffix_regexp = re.search(r"(/@@.*)", path)
    if suffix_regexp:
        suffix = suffix_regexp.group(0)
    if suffix:
        path = path.replace(suffix, '')
    obj = portal.unrestrictedTraverse(path, None)
    if obj is None or obj == portal:
        return link
    segments = path.split("/")
    if not suffix:
        while not IUUIDAware.providedBy(obj):
            obj = aq_parent(obj)
            if obj is None:
                break
            suffix += "/" + segments.pop()
    # check if obj is wrong because of acquisition
    if not obj or "/".join(obj.getPhysicalPath()) != "/".join(segments):
        return link
    href = relative_up * "../" + "resolveuid/" + IUUID(obj)
    if suffix:
        href += suffix
    return href
