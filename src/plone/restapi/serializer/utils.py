from plone.app.uuid.utils import uuidToObject
from plone.outputfilters.browser.resolveuid import uuidToURL
from plone.restapi.interfaces import IObjectPrimaryFieldTarget
from zope.component import queryMultiAdapter

import re


RESOLVEUID_RE = re.compile("^[./]*resolve[Uu]id/([^/]*)/?(.*)$")


# Takes the resolveID URL and returns a URL to the actual object
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
        # Pass unrestricted flag as true so the object is accessible.
        # At uuidToObject(), this leads to unrestrictedTraverse() to be invoked instead of restrictedTraverse().
        target_object = uuidToObject(uid, unrestricted=True)
        if target_object:
            adapter = queryMultiAdapter(
                (target_object, target_object.REQUEST), IObjectPrimaryFieldTarget
            )
            if adapter and adapter():
                href = adapter()
    return href
