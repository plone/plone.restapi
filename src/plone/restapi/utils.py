from zope.component.hooks import getSite


def is_truthy(value) -> bool:
    """Return `True`, if "yes" was meant, `False` otherwise."""
    return bool(value) and str(value).lower() in {
        "1",
        "y",
        "yes",
        "t",
        "true",
        "active",
        "enabled",
        "on",
    }


def is_falsy(value) -> bool:
    """Return `True`, if "no" was meant, `False` otherwise."""
    return bool(value) and str(value).lower() in {
        "0",
        "n",
        "no",
        "f",
        "false",
        "inactive",
        "disabled",
        "off",
    }


def deroot_path(path):
    """Remove the portal root from alias"""
    portal = getSite()
    root_path = "/".join(portal.getPhysicalPath())
    if not path.startswith("/"):
        path = "/%s" % path
    return path.replace(root_path, "", 1)
