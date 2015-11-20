# -*- coding: utf-8 -*-


def append_json_to_links(result):
    """
    """
    if '@id' in result:
        result['@id'] = '{0}?format=json'.format(result['@id'])
    if 'member' in result:
        for index, item in enumerate(result['member']):
            if '@id' in item:
                result['member'][index]['@id'] = '{0}?format=json'.format(
                    result['member'][index]['@id']
                )
    if 'parent' in result and result != {} and '@id' in result['parent']:
        result['parent']['@id'] = '{0}?format=json'.format(
            result['parent']['@id']
        )
    return result
