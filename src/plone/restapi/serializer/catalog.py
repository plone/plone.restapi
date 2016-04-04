# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from Products.ZCatalog.Lazy import Lazy
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(Lazy, Interface)
class LazyCatalogResultSerializer(object):
    """Serializes a ZCatalog resultset (one of the subclasses of `Lazy`) to
    a Python data structure that can in turn be serialized to JSON.
    """

    def __init__(self, lazy_resultset, request):
        self.lazy_resultset = lazy_resultset
        self.request = request

    def __call__(self):
        results = {}
        results['items_count'] = self.lazy_resultset.actual_result_count
        results['member'] = []

        for brain in self.lazy_resultset:
            brain_summary = getMultiAdapter(
                (brain, self.request), ISerializeToJsonSummary)()
            results['member'].append(brain_summary)
        return results
