# -*- coding: utf-8 -*-
from zope.schema import getFields
from zope.interface import providedBy
from plone.behavior.interfaces import IBehaviorAssignable


def get_object_schema(obj):

    # Iterate over all interfaces that are provided by the object and filter
    # out all attributes that start with '_' or 'manage'.
    for iface in providedBy(obj).flattened():
        for name, field in getFields(iface).items():
            no_underscore_method = not name.startswith('_')
            no_manage_method = not name.startswith('manage')
            if no_underscore_method and no_manage_method:
                yield name, field

    # Iterate over all behaviors that are assigned to the object.
    assignable = IBehaviorAssignable(obj, None)
    if assignable:
        for behavior in assignable.enumerateBehaviors():
            for name, field in getFields(behavior.interface).items():
                yield name, field


def underscore_to_camelcase(underscore_string):
    return ''.join(
        x for x in underscore_string.title() if not x.isspace()
    ).replace('_', '')


def append_json_to_links(result):
    """
    """
    if '@id' in result:
        result['@id'] = '{0}/@@json'.format(result['@id'])
    if 'member' in result:
        for index, item in enumerate(result['member']):
            if '@id' in item:
                result['member'][index]['@id'] = '{0}/@@json'.format(
                    result['member'][index]['@id']
                )
    if 'parent' in result and result != {} and '@id' in result['parent']:
        result['parent']['@id'] = '{0}/@@json'.format(
            result['parent']['@id']
        )
    return result
