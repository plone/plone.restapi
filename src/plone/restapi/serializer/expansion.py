from plone.restapi.interfaces import IExpandableElement
from zope.component import getAdapters


def expandable_elements(context, request):
    """Returns a dict containing all expandable elements."""
    expands = request.form.get("expand", [])
    if isinstance(expands, str):
        if "," in expands:
            # use of expands (with commas) was deprecated in plone.restapi 8
            # undeprecated with plone.restapi 9
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
