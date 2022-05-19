from contextlib import contextmanager
from plone.scale import storage
from Products.CMFCore.utils import getToolByName
from unittest.mock import patch
from urllib.parse import urlparse

import quopri


def result_paths(results):
    """Helper function to make it easier to write list-based assertions on
    result sets from the search endpoint.
    """

    def get_path(item):
        if "getPath" in item:
            return item["getPath"]
        return urlparse(item["@id"]).path

    return [get_path(item) for item in results["items"]]


def add_catalog_indexes(portal, indexes):
    """Add all `indexes` to the plone catalog.

    The argument `indexes` can be a tuple of length two when only name and
    meta_type are required. It also supports a tuple of length three when
    additional arguments are required to add an index (e.g. when adding a
    `ZCTextIndex` index).

    """
    catalog = getToolByName(portal, "portal_catalog")
    current_indexes = catalog.indexes()

    indexables = []
    for name, index_type in indexes:
        if name not in current_indexes:
            catalog.addIndex(name, index_type)
            indexables.append(name)
    if len(indexables) > 0:
        catalog.manage_reindexIndex(ids=indexables)


def ascii_token(text):
    """Turn a text (unicode in Py2, str in Py3) into a ASCII-only
    bytestring that is safe to use in term tokens.
    """
    return quopri.encodestring(text.encode("utf-8"))


@contextmanager
def patch_scale_uuid(value):
    """Patch plone.scale to use a hard coded value as unique id.

    Until plone.scale 4.0.0a3 (2022-05-09) this goes via the uuid4 function.
    For later versions we need to patch the new hash_key method.

    We also patch the _modified_since method to always return True.
    Otherwise you may get info from a different scale back,
    precisely because we give all scales the same "unique" id,
    which then is of course no longer unique, making the logic unstable.
    This is needed for the newer plone.scale versions,
    but should be perfectly fine for the older ones.
    """
    if hasattr(storage.AnnotationStorage, "hash_key"):
        to_patch = storage.AnnotationStorage
        name = "hash_key"
    else:
        to_patch = storage
        name = "uuid4"
    with patch.object(to_patch, name, return_value=value):
        with patch.object(
            storage.AnnotationStorage, "_modified_since", return_value=True
        ):
            yield
