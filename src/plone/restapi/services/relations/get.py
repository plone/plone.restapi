from AccessControl.SecurityManagement import getSecurityManager
from collections import defaultdict
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.relationhelper import get_relations_stats
from zc.relation.interfaces import ICatalog
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.globalrequest import getRequest
from zope.intid.interfaces import IIntIds


def make_summary(obj, request):
    """Add UID to metadata_fields."""
    metadata_fields = request.form.get("metadata_fields", []) or []
    if not isinstance(metadata_fields, list):
        metadata_fields = [metadata_fields]
    metadata_fields.append("UID")
    request.form["metadata_fields"] = list(set(metadata_fields))
    summary = getMultiAdapter((obj, request), ISerializeToJsonSummary)()
    return json_compatible(summary)


# Loosely based on plone.api.relation.get
def get_relations(
    source=None,
    target=None,
    relationship=None,
    request=None,
    unrestricted=False,
):
    results = defaultdict(list)
    if request is None:
        request = getRequest()
    intids = getUtility(IIntIds)
    relation_catalog = queryUtility(ICatalog)
    if relation_catalog is None:
        return results

    query = {}
    if source is not None:
        query["from_id"] = intids.getId(source)
    if target is not None:
        query["to_id"] = intids.getId(target)
    if relationship is not None:
        query["from_attribute"] = relationship

    if not unrestricted:
        checkPermission = getSecurityManager().checkPermission

    for relation in relation_catalog.findRelations(query):
        if relation.isBroken():
            continue

        source_obj = relation.from_object
        target_obj = relation.to_object

        if not unrestricted:
            can_view = checkPermission("View", source_obj) and checkPermission(
                "View", target_obj
            )
            if not can_view:
                continue

        results[relation.from_attribute].append(
            {
                "source": make_summary(source_obj, request),
                "target": make_summary(target_obj, request),
            }
        )
    return results


def relation_stats():
    rels, broken = get_relations_stats()
    results = {"relations": rels, "broken": broken}
    return json_compatible(results)


class GetRelations(Service):
    """Get relations or stats

        source: UID of content item
        target: UID of content item
        relation: name of a relation

    Returns:
        dictionary of relations grouped by relation name
    """

    def __init__(self, context, request):
        super().__init__(context, request)
        self.sm = getSecurityManager()

    def reply(self):
        source = self.request.get("source", None)
        target = self.request.get("target", None)
        relationship = self.request.get("relation", None)

        if not source and not target and not relationship:
            try:
                stats = relation_stats()
                stats[
                    "@id"
                ] = f'{self.request["SERVER_URL"]}{self.request.environ["REQUEST_URI"]}'
                return stats

            except Unauthorized as exception:
                return self.reply_no_content(status=401)

        catalog = getToolByName(self.context, "portal_catalog")
        if source:
            brains = catalog(UUID=source)
            if brains:
                source = brains[0].getObject()
            else:
                return self.reply_no_content(status=404)

        if target:
            brains = catalog(UUID=target)
            if brains:
                target = brains[0].getObject()
            else:
                return self.reply_no_content(status=404)

        data = get_relations(
            source=source,
            target=target,
            relationship=relationship,
            # unrestricted=True,
            request=self.request,
        )

        return {
            "@id": f'{self.request["SERVER_URL"]}{self.request.environ["REQUEST_URI"]}',
            "items": data,
            "items_total": dict([(el, len(data[el])) for el in data]),
        }
