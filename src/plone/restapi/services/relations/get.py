from AccessControl.SecurityManagement import getSecurityManager
from collections import defaultdict
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.restapi.services.relations import api_relation_create
from plone.restapi.services.relations import plone_api_content_get
from zc.relation.interfaces import ICatalog
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.globalrequest import getRequest
from zope.intid.interfaces import IIntIds
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory

import plone.protect.interfaces

MAX = 2500

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
    summary = json_compatible(summary)
    ("image_scales" in summary) and summary.pop("image_scales", None)
    ("image_field" in summary) and summary.pop("image_field", None)
    return summary


def get_relations(
    source=None,
    target=None,
    relationship=None,
    request=None,
    unrestricted=False,
    onlyBroken=False,
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

    if max:
        try:
            max = int(max)
        except TypeError as e:
            raise ValueError(str(e))
    count = 0
    relations = relation_catalog.findRelations(query)
    for relation in relations:
        if relation.isBroken():
            if not onlyBroken:
                continue
        else:
            if onlyBroken:
                continue
        count += 1
        if max and count > max:
            break

        source_obj = relation.from_object
        target_obj = relation.to_object

        if not unrestricted:
            can_view = (not source_obj or checkPermission("View", source_obj)) and (
                not target_obj or checkPermission("View", target_obj)
            )
            if not can_view:
                continue

        if onlyBroken:
            results[relation.from_attribute].append(
                [
                    source_obj and source_obj.absolute_url() or "",
                    target_obj and target_obj.absolute_url() or "",
                ]
            )
        else:
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


def getBrokenRelationNames():
    relation_catalog = queryUtility(ICatalog)
    if relation_catalog is None:
        return []

    relations = relation_stats()
    return relations["broken"] and relations["broken"].keys() or []


def getStaticCatalogVocabularyQuery(vocabularyFactoryName):
    factory = queryUtility(IVocabularyFactory, vocabularyFactoryName)
    if factory:
        return factory().query
    return


class GetRelations(Service):
    """Get relations or stats

        source: UID of content item
        target: UID of content item
        relation: name of a relation
        onlyBroken: boolean: dictionary with broken relations per relation type
        max: integer: maximum of results

    Returns:
        stats if no parameter, else relations
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
        max = self.request.get("max", False)
        onlyBroken = self.request.get("onlyBroken", False)

        # Rebuild relations with or without regenerating intids
        if rebuild:
            if rebuild_relations:
                flush = self.request.get("flush", False) and True
                try:
                    print("*** Now rebuild relations. flush:", flush)
                    rebuild_relations(flush_and_rebuild_intids=flush)
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

        # Get broken relations for all relation types
        if onlyBroken:
            data = {}
            relationNames = getBrokenRelationNames()
            for relationName in relationNames:
                foo = get_relations(relationship=relationName, onlyBroken=True)
                data.update(foo)
            return {
                "@id": f'{self.request["SERVER_URL"]}{self.request.environ["REQUEST_URI"]}',
                "items": data,
                "items_total": dict([(el, len(data[el])) for el in data]),
            }

        # Stats
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

        # Query relations
        if source:
            if source[0:1] == "/":
                source = plone_api_content_get(path=source)
            else:
                source = plone_api_content_get(UID=source)
            if not source:
                return self.reply_no_content(status=404)

        if target:
            if target[0:1] == "/":
                target = plone_api_content_get(path=target)
            else:
                target = plone_api_content_get(UID=target)
            if not target:
                return self.reply_no_content(status=404)

        data = get_relations(
            source=source,
            target=target,
            relationship=relationship,
            max=max,
            request=self.request,
        )

        result = {
            "@id": f'{self.request["SERVER_URL"]}{self.request.environ["REQUEST_URI"]}',
            "items": data,
            "items_total": dict([(el, len(data[el])) for el in data]),
        }

        if relationship:
            scvq = getStaticCatalogVocabularyQuery(relationship)
            result["staticCatalogVocabularyQuery"] = scvq
            result["readonly"] = not api_relation_create

        return result
