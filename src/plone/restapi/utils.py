# -*- coding: utf-8 -*-
from zope.schema import getFields
from zope.schema import TextLine
from zope.interface import providedBy
from plone.behavior.interfaces import IBehaviorAssignable


def get_object_schema(obj):
    object_schema = set()

    # Iterate over all interfaces that are provided by the object and filter
    # out all attributes that start with '_' or 'manage'.
    for iface in providedBy(obj).flattened():
        for name, field in getFields(iface).items():
            no_underscore_method = not name.startswith('_')
            no_manage_method = not name.startswith('manage')
            if no_underscore_method and no_manage_method:
                if name not in object_schema:
                    object_schema.add(name)
                    yield name, field

    # Iterate over all behaviors that are assigned to the object.
    assignable = IBehaviorAssignable(obj, None)
    if assignable:
        for behavior in assignable.enumerateBehaviors():
            for name, field in getFields(behavior.interface).items():
                if name not in object_schema:
                    object_schema.add(name)
                    yield name, field

    # The portal_type is declared in IDexterityFactory and not included in the
    # interfaces that are provided by the object.
    # https://github.com/plone/plone.dexterity/blob/master/plone/dexterity/interfaces.py#L94  # noqa
    yield 'portal_type', TextLine


def underscore_to_camelcase(underscore_string):
    return ''.join(
        x for x in underscore_string.title() if not x.isspace()
    ).replace('_', '')
