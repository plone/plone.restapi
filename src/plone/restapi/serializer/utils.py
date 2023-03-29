from plone.restapi.interfaces import IObjectPrimaryFieldTarget
from zope.component import queryMultiAdapter

import re


try:
    from plone.app.uuid.utils import uuidToObject
    from plone.app.uuid.utils import uuidToURL

except ImportError:
    # Plone 5.2
    from plone.outputfilters.browser.resolveuid import uuidToObject as old_uuidToObject
    from plone.outputfilters.browser.resolveuid import uuidToURL

    def uuidToObject(uid, unrestricted=False):
        return old_uuidToObject(uid)


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
        target_object = uuidToObject(uid, unrestricted=True)
        if target_object:
            adapter = queryMultiAdapter(
                (target_object, target_object.REQUEST),
                IObjectPrimaryFieldTarget,
            )
            if adapter and adapter():
                href = adapter()
    return href
