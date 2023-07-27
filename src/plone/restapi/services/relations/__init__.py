try:
    from plone.api.relation import create as api_relation_create
    from plone.api.relation import delete as api_relation_delete
except ImportError:
    api_relation_create = None
    api_relation_delete = None

from plone.app.uuid.utils import uuidToObject
from Products.CMFCore.DynamicType import DynamicType
from zope.component.hooks import getSite


def plone_api_content_get(path=None, UID=None):
    """Get an object.

    copy pasted from plone.api
    """
    if path:
        site = getSite()
        site_absolute_path = "/".join(site.getPhysicalPath())
        if not path.startswith("{path}".format(path=site_absolute_path)):
            path = "{site_path}{relative_path}".format(
                site_path=site_absolute_path,
                relative_path=path,
            )
        try:
            content = site.restrictedTraverse(path)
        except (KeyError, AttributeError):
            return None  # When no object is found don't raise an error
        else:
            # Only return a content if it implements DynamicType,
            # which is true for Dexterity content and Comment (plone.app.discussion)
            return content if isinstance(content, DynamicType) else None

    elif UID:
        return uuidToObject(UID)
