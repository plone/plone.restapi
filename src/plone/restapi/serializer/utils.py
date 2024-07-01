from plone.app.uuid.utils import uuidToCatalogBrain
from plone.dexterity.schema import lookup_fti
from plone.restapi.interfaces import IObjectPrimaryFieldTarget
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from zope.i18n import translate

import re


RESOLVEUID_RE = re.compile("^(?:|.*/)resolve[Uu]id/([^/#]*)?(.*)?$")


def resolve_uid(path):
    """Resolves a resolveuid URL into a tuple of absolute URL and catalog brain.

    If the original path is not found (including external URLs),
    it will be returned unchanged and the brain will be None.
    """
    if not path:
        return "", None
    match = RESOLVEUID_RE.match(path)
    if match is None:
        return path, None

    uid, suffix = match.groups()
    brain = uuidToCatalogBrain(uid)
    if brain is None:
        return path, None
    href = brain.getURL()
    if suffix:
        return href + suffix, brain
    target_object = brain._unrestrictedGetObject()
    adapter = queryMultiAdapter(
        (target_object, target_object.REQUEST),
        IObjectPrimaryFieldTarget,
    )
    if adapter:
        a_href = adapter()
        if a_href:
            return a_href, None
    return href, brain


def uid_to_url(path):
    path, _brain = resolve_uid(path)
    return path


def get_portal_type_title(portal_type):
    fti = lookup_fti(portal_type)
    request = getRequest()
    if request:
        return translate(getattr(fti, "Title", lambda: portal_type)(), context=request)
    return getattr(fti, "Title", lambda: portal_type)()
