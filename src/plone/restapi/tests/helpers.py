# -*- coding: utf-8 -*-
from urlparse import urlparse


def result_paths(results):
    """Helper function to make it easier to write list-based assertions on
    result sets from the search endpoint.
    """
    def get_path(item):
        if 'getPath' in item:
            return item['getPath']
        return urlparse(item['@id']).path

    return [get_path(item) for item in results['member']]
