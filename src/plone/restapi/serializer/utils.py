from plone.app.uuid.utils import uuidToCatalogBrain
from plone.restapi.interfaces import IObjectPrimaryFieldTarget
from zope.component import queryMultiAdapter

import re


RESOLVEUID_RE = re.compile("^[./]*resolve[Uu]id/([^/]*)/?(.*)$")


def uid_to_url(path):
    """turns a resolveuid url into a real url.

    This uses the catalog first, but wake up the object to check if there is
    an IObjectPrimaryFieldTarget on this object. If so, it will return the
    target url instead of the object url.
    """
    if not path:
        return ""
    match = RESOLVEUID_RE.match(path)
    if match is None:
        return path

    uid, suffix = match.groups()
    brain = uuidToCatalogBrain(uid)
    if brain is None:
        return path
    href = brain.getURL()
    if suffix:
        return href + "/" + suffix
    target_object = brain._unrestrictedGetObject()
    adapter = queryMultiAdapter(
        (target_object, target_object.REQUEST),
        IObjectPrimaryFieldTarget,
    )
    if adapter:
        a_href = adapter()
        if a_href:
            return a_href
    return href
