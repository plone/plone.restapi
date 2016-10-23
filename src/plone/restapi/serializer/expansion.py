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
            res.update(element[1](expand=True))
        else:
            res.update(element[1](expand=False))
    return res
