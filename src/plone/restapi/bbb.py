try:
    from plone.base.defaultpage import is_default_page
    from plone.base.interfaces import IConstrainTypes
    from plone.base.interfaces import IEditingSchema
    from plone.base.interfaces import IImagingSchema
    from plone.base.interfaces import ILanguage
    from plone.base.interfaces import IMailSchema
    from plone.base.interfaces import IMigratingPloneSiteRoot
    from plone.base.interfaces import INavigationRoot
    from plone.base.interfaces import INavigationSchema
    from plone.base.interfaces import INonInstallable
    from plone.base.interfaces import INonStructuralFolder
    from plone.base.interfaces import IPloneSiteRoot
    from plone.base.interfaces import ISearchSchema
    from plone.base.interfaces import ISecuritySchema
    from plone.base.interfaces import ISelectableConstrainTypes
    from plone.base.interfaces import ISiteSchema
    from plone.base.interfaces import ITestCasePloneSiteRoot
    from plone.base.navigationroot import get_navigation_root
    from plone.base.utils import base_hasattr
    from plone.base.utils import safe_callable
    from plone.base.utils import safe_hasattr
    from plone.base.utils import safe_text
except ImportError:
    # BBB Plone 5.2
    from plone.app.layout.navigation.interfaces import INavigationRoot
    from plone.app.layout.navigation.root import (
        getNavigationRoot as get_navigation_root,
    )
    from Products.CMFPlone.defaultpage import is_default_page
    from Products.CMFPlone.interfaces import IConstrainTypes
    from Products.CMFPlone.interfaces import IEditingSchema
    from Products.CMFPlone.interfaces import IImagingSchema
    from Products.CMFPlone.interfaces import ILanguage
    from Products.CMFPlone.interfaces import IMailSchema
    from Products.CMFPlone.interfaces import IMigratingPloneSiteRoot
    from Products.CMFPlone.interfaces import INavigationSchema
    from Products.CMFPlone.interfaces import INonInstallable
    from Products.CMFPlone.interfaces import INonStructuralFolder
    from Products.CMFPlone.interfaces import IPloneSiteRoot
    from Products.CMFPlone.interfaces import ISearchSchema
    from Products.CMFPlone.interfaces import ISecuritySchema
    from Products.CMFPlone.interfaces import ISelectableConstrainTypes
    from Products.CMFPlone.interfaces import ISiteSchema
    from Products.CMFPlone.interfaces import ITestCasePloneSiteRoot
    from Products.CMFPlone.utils import base_hasattr
    from Products.CMFPlone.utils import safe_callable
    from Products.CMFPlone.utils import safe_hasattr
    from Products.CMFPlone.utils import safe_text


# Backwards compatibility for old Plone versions that do not use plone.base.
# See https://github.com/plone/plone.restapi/issues/1960 and
# https://github.com/plone/plone.base/pull/112
# remove this when we deprecate support for Plone 5.2 and 6.0

try:
    from plone.base.utils import boolean_value
except ImportError:
    from typing import Optional

    # BBB Plone without boolean_value in plone.base

    def is_truthy(value) -> bool:
        """
        Return `True`, if value is a boolean `True` or an integer `1` or
        a string that looks like "yes", `False` otherwise.
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value == 1
        str_value = str(value).lower().strip()
        return str_value in {
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
        """
        Return `True`, if value is a boolean `False` or an integer `0` or
        a string that looks like "no", `False` otherwise.
        """
        if isinstance(value, bool):
            return not value
        if isinstance(value, int):
            return value == 0
        str_value = str(value).lower().strip()
        return str_value in {
            "0",
            "n",
            "no",
            "f",
            "false",
            "inactive",
            "disabled",
            "off",
        }

    def boolean_value(value, default: Optional[bool] = None) -> bool:
        """Return a boolean value for the given input.

        Raises ValueError if the input was not recognized as a boolean.
        """
        if is_truthy(value):
            return True
        if is_falsy(value):
            return False
        if isinstance(default, bool):
            return default
        raise ValueError(f"Could not parse value {value!r} as boolean")
