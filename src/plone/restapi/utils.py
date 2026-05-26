from zope.component.hooks import getSite


def deroot_path(path):
    """Remove the portal root from alias"""
    portal = getSite()
    root_path = "/".join(portal.getPhysicalPath())
    if not path.startswith("/"):
        path = "/%s" % path
    return path.replace(root_path, "", 1)
