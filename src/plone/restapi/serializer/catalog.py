from plone.registry.interfaces import IRegistry
from plone.restapi.batching import HypermediaBatch
from plone.restapi.bbb import INavigationSchema
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
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
class LazyCatalogResultSerializer:
    """Serializes a ZCatalog resultset (one of the subclasses of `Lazy`) to
    a Python data structure that can in turn be serialized to JSON.
    """

    def __init__(self, lazy_resultset, request):
        self.lazy_resultset = lazy_resultset
        self.request = request

    def _get_results_to_batch(self):
        """Return the result set to batch, filtering by exclude_from_nav if needed (fixes plone/volto#1340)."""
        results = self.lazy_resultset
        try:
            registry = getUtility(IRegistry)
            navigation_settings = registry.forInterface(
                INavigationSchema, prefix="plone"
            )
            if not navigation_settings.show_excluded_items:
                results = [
                    b for b in results if not getattr(b, "exclude_from_nav", False)
                ]
        except Exception:
            pass
        return results

    def __call__(self, fullobjects=False):
        results_to_batch = self._get_results_to_batch()
        batch = HypermediaBatch(self.request, results_to_batch)

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
                    obj = brain.getObject()
                except KeyError:
                    # Guard in case the brain returned refers to an object that doesn't
                    # exists because it failed to uncatalog itself or the catalog has
                    # stale cataloged objects for some reason
                    log.warning(
                        "Brain getObject error: {} doesn't exist anymore".format(
                            brain.getPath()
                        )
                    )
                    continue

                result = getMultiAdapter((obj, self.request), ISerializeToJson)(
                    include_items=False
                )
            else:
                result = getMultiAdapter(
                    (brain, self.request), ISerializeToJsonSummary
                )()

            results["items"].append(result)

        return results
