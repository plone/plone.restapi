# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from zope.component import getAdapters


def expandable_elements(context, request):
    """Returns a dict containing all expandable elements.
    """
    expands = request.form.get('expand', '').split(',')
    elements = getAdapters((context, request), IExpandableElement)
    res = {}
    for element in elements:
        if element[0] in expands:
            update_dict_recursively(res, element[1](expand=True))
        else:
            update_dict_recursively(res, element[1](expand=False))
    return {"@components": res}


def update_dict_recursively(d, u):
    for key, value in u.iteritems():
        if isinstance(value, dict):
            r = update_dict_recursively(d.get(key, {}), value)
            d[key] = r
        else:
            d[key] = u[key]
    return d
