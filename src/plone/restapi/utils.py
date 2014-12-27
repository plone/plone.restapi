# -*- coding: utf-8 -*-
from zope.schema import getFields
from zope.interface import providedBy
from plone.behavior.interfaces import IBehaviorAssignable


def get_object_schema(obj):
    object_schema = set()
    for iface in providedBy(obj).flattened():
        for name, field in getFields(iface).items():
            no_underscore_method = not name.startswith('_')
            no_manage_method = not name.startswith('manage')
            if no_underscore_method and no_manage_method:
                if name not in object_schema:
                    object_schema.add(name)
                    yield name, field

    assignable = IBehaviorAssignable(obj, None)
    if assignable:
        for behavior in assignable.enumerateBehaviors():
            for name, field in getFields(behavior.interface).items():
                if name not in object_schema:
                    object_schema.add(name)
                    yield name, field


def underscore_to_camelcase(underscore_string):
    return ''.join(
        x for x in underscore_string.title() if not x.isspace()
    ).replace('_', '')
