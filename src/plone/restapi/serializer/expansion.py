from plone.restapi.interfaces import IExpandableElement
from zope.component import getAdapters

import warnings


def expandable_elements(context, request):
    """Returns a dict containing all expandable elements."""
    expands = request.form.get("expand", [])
    if isinstance(expands, str):
        if "," in expands:
            # deprecated use of expands (with commas)
            warnings.warn(
                "``expand`` as a string parameter separated with commas is deprecated and will be removed in plone.restapi 9.0. Use ``expand:list`` instead.",
                DeprecationWarning,
            )
            expands = expands.split(",")
        else:
            # allow still the use of non marked :list parameters present
            expands = [expands]

    elements = getAdapters((context, request), IExpandableElement)
    res = {}
    for element in elements:
        if element[0] in expands:
            update_dict_recursively(res, element[1](expand=True))
        else:
            update_dict_recursively(res, element[1](expand=False))
    return {"@components": res}


def update_dict_recursively(d, u):
    for key, value in u.items():
        if isinstance(value, dict):
            r = update_dict_recursively(d.get(key, {}), value)
            d[key] = r
        else:
            d[key] = u[key]
    return d
