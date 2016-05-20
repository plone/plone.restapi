# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from urlparse import urlparse


def result_paths(results):
    """Helper function to make it easier to write list-based assertions on
    result sets from the search endpoint.
    """
    def get_path(item):
        if 'getPath' in item:
            return item['getPath']
        return urlparse(item['@id']).path

    return [get_path(item) for item in results['items']]


def add_catalog_indexes(portal, indexes):
    """Add all `indexes` to the plone catalog.

    The argument `indexes` can be a tuple of length two when only name and
    meta_type are required. It also supports a tuple of length three when
    additional arguments are required to add an index (e.g. when adding a
    `ZCTextIndex` index).

    """
    catalog = getToolByName(portal, 'portal_catalog')
    current_indexes = catalog.indexes()

    indexables = []
    for name, index_type in indexes:
        if name not in current_indexes:
            catalog.addIndex(name, index_type)
            indexables.append(name)
    if len(indexables) > 0:
        catalog.manage_reindexIndex(ids=indexables)
