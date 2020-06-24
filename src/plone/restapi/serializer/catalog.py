# -*- coding: utf-8 -*-
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

import logging

try:
    from ZTUtils.Lazy import Lazy
except ImportError:
    from Products.ZCatalog.Lazy import Lazy

log = logging.getLogger(__name__)


@implementer(ISerializeToJson)
@adapter(Lazy, Interface)
class LazyCatalogResultSerializer(object):
    """Serializes a ZCatalog resultset (one of the subclasses of `Lazy`) to
    a Python data structure that can in turn be serialized to JSON.
    """

    def __init__(self, lazy_resultset, request):
        self.lazy_resultset = lazy_resultset
        self.request = request

    def __call__(self, fullobjects=False):
        batch = HypermediaBatch(self.request, self.lazy_resultset)

        results = {}
        results["@id"] = batch.canonical_url
        results["items_total"] = batch.items_total
        links = batch.links
        if links:
            results["batching"] = links

        results["items"] = []
        for brain in batch:
            if fullobjects:
                try:
                    result = getMultiAdapter(
                        (brain.getObject(), self.request), ISerializeToJson
                    )(include_items=False)
                except KeyError:
                    # Guard in case the brain returned refers to an object that doesn't
                    # exists because it failed to uncatalog itself or the catalog has
                    # stale cataloged objects for some reason
                    log.warning(
                        "Brain getObject error: {} doesn't exist anymore".format(
                            brain.getPath()
                        )
                    )
            else:
                result = getMultiAdapter(
                    (brain, self.request), ISerializeToJsonSummary
                )()

            results["items"].append(result)

        return results
