from AccessControl.SecurityManagement import getSecurityManager
from collections import defaultdict
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.relationhelper import get_relations_stats
from zc.relation.interfaces import ICatalog
from zExceptions import BadRequest, Unauthorized
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.globalrequest import getRequest
from zope.intid.interfaces import IIntIds
from zope.interface import alsoProvides

import plone.protect.interfaces

try:
    from Products.CMFPlone.relationhelper import get_relations_stats
except ImportError:
    try:
        from collective.relationhelpers.api import get_relations_stats
    except ImportError:
        get_relations_stats = None

try:
    from Products.CMFPlone.relationhelper import rebuild_relations
except ImportError:
    try:
        from collective.relationhelpers.api import rebuild_relations
    except ImportError:
        rebuild_relations = None


def make_summary(obj, request):
    """Add UID to metadata_fields."""
    metadata_fields = request.form.get("metadata_fields", []) or []
    if not isinstance(metadata_fields, list):
        metadata_fields = [metadata_fields]
    metadata_fields.append("UID")
    request.form["metadata_fields"] = list(set(metadata_fields))
    summary = getMultiAdapter((obj, request), ISerializeToJsonSummary)()
    return json_compatible(summary)


def get_relations(
    source=None,
    target=None,
    relationship=None,
    request=None,
    unrestricted=False,
    max=None,
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

    relations = relation_catalog.findRelations(query)
    if max:
        relations = relations[: max - 1]
    for relation in relations:
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
    if get_relations_stats is not None:
        rels, broken = get_relations_stats()
        results = {"relations": rels, "broken": broken}
        return json_compatible(results)
    else:
        raise ImportError


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

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        source = self.request.get("source", None)
        target = self.request.get("target", None)
        relationship = self.request.get("relation", None)
        rebuild = self.request.get("rebuild", False)

        if rebuild:
            if rebuild_relations:
                flush = self.request.get("flush", None) and True or False
                try:
                    # print("Now rebuild relations. flush:", flush)
                    rebuild_relations(flush_and_rebuild_intids=flush)
                    # raise BadRequest("bä")
                    return self.reply_no_content()
                except Exception as e:
                    self.request.response.setStatus(500)
                    return dict(
                        error=dict(
                            # type="ImportError",
                            message=str(e),
                        )
                    )
            else:
                self.request.response.setStatus(501)
                return dict(
                    error=dict(
                        type="ImportError",
                        message="Relationhelpers not available. Install collective.relationhelpers or upgrade to Plone 6!",
                    )
                )

        if not source and not target and not relationship:
            try:
                stats = relation_stats()
                stats[
                    "@id"
                ] = f'{self.request["SERVER_URL"]}{self.request.environ["REQUEST_URI"]}'
                return stats
            except ImportError:
                self.request.response.setStatus(501)
                return dict(
                    error=dict(
                        type="ImportError",
                        message="Relationhelpers not available. Install collective.relationhelpers or upgrade to Plone 6!",
                    )
                )
            except Unauthorized:
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
