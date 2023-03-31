from plone.outputfilters.browser.resolveuid import uuidToObject
from plone.outputfilters.browser.resolveuid import uuidToURL
from plone.dexterity.interfaces import IDexterityFTI
from plone.restapi.interfaces import IObjectPrimaryFieldTarget
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.i18n import translate

import re


RESOLVEUID_RE = re.compile("^[./]*resolve[Uu]id/([^/]*)/?(.*)$")


def uid_to_url(path):
    if not path:
        return ""
    match = RESOLVEUID_RE.match(path)
    if match is None:
        return path

    uid, suffix = match.groups()
    href = uuidToURL(uid)
    if href is None:
        return path
    if suffix:
        href += "/" + suffix
    else:
        target_object = uuidToObject(uid)
        if target_object:
            adapter = queryMultiAdapter(
                (target_object, target_object.REQUEST),
                IObjectPrimaryFieldTarget,
            )
            if adapter and adapter():
                href = adapter()
    return href


def get_portal_type(portal_type, request=None):
    fti = queryUtility(IDexterityFTI, name=portal_type)
    if request:
        return translate(getattr(fti, "Title", lambda: portal_type)(), context=request)
    return getattr(fti, "Title", lambda: portal_type)()
