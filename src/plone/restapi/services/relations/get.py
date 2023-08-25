from AccessControl.SecurityManagement import getSecurityManager
from collections import defaultdict
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.restapi.services.relations import api_relation_create
from plone.restapi.services.relations import plone_api_content_get
from Products.CMFCore.utils import getToolByName
from zc.relation import catalog as zcr_catalog
from zc.relation.interfaces import ICatalog
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.intid.interfaces import IIntIds
from zope.intid.interfaces import IntIdMissingError
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


def make_summary(obj, request):
    """Add UID to metadata_fields."""
    metadata_fields = request.form.get("metadata_fields", []) or []
    if not isinstance(metadata_fields, list):
        metadata_fields = [metadata_fields]
    metadata_fields.append("UID")
    request.form["metadata_fields"] = list(set(metadata_fields))
    summary = getMultiAdapter((obj, request), ISerializeToJsonSummary)()
    summary = json_compatible(summary)
    return summary


def get_relations(
    sources=None,
    targets=None,
    relationship=None,
    request=None,
    unrestricted=False,
    onlyBroken=False,
    max=None,
):
    """Get valid relations."""
    results = defaultdict(list)
    if request is None:
        request = getRequest()
    intids = getUtility(IIntIds)
    relation_catalog = queryUtility(ICatalog)
    if relation_catalog is None:
        return results

    query = {}
    if sources is not None:
        iids = []
        for el in sources:
            try:
                iids.append(intids.getId(el))
            except IntIdMissingError:
                continue
        query["from_id"] = zcr_catalog.any(*iids)

    if targets is not None:
        iids = []
        for el in targets:
            try:
                iids.append(intids.getId(el))
            except IntIdMissingError:
                continue
        query["to_id"] = zcr_catalog.any(*iids)
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
    relations = list(relation_catalog.findRelations(query))

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
                    source_obj and source_obj.absolute_url() or relation.from_path,
                    target_obj and target_obj.absolute_url() or relation.to_path,
                ]
            )
        else:
            # Exclude relations without source or target.
            # Dispensable with https://github.com/zopefoundation/z3c.relationfield/pull/24
            if not source_obj or not target_obj:
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
        results = {"stats": rels, "broken": broken}
        return json_compatible(results)
    else:
        raise NotImplementedError("Not implemented in this version of Plone")


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
        max: integer: maximum of results
        onlyBroken: boolean: dictionary with broken relations per relation type
        query_source: Restrict relations by path or SearchableText
        query_target: Restrict relations by path or SearchableText

    Returns:
        stats if no parameter, else relations
    """

    def __init__(self, context, request):
        super().__init__(context, request)

    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
        source = self.request.get("source", None)
        target = self.request.get("target", None)
        relationship = self.request.get("relation", None)
        max = self.request.get("max", False)
        onlyBroken = self.request.get("onlyBroken", False)
        query_source = self.request.get("query_source", None)
        query_target = self.request.get("query_target", None)

        targets = None
        sources = None

        catalog = getToolByName(self.context, "portal_catalog")
        portal = getSite()

        # Get broken relations for all relation types
        if onlyBroken:
            relationNames = getBrokenRelationNames()
            if len(relationNames) == 0:
                return self.reply_no_content(status=204)
            result = {
                "@id": f"{self.context.absolute_url()}/@relations?onlyBroken=true",
                "relations": {},
            }
            for relationName in relationNames:
                rels = get_relations(relationship=relationName, onlyBroken=True)
                result["relations"][relationName] = {
                    "items": rels[relationName],
                    "items_total": len(rels[relationName]),
                }
            return result

        # Stats
        if not source and not target and not relationship:
            try:
                stats = relation_stats()
                stats["@id"] = f"{self.context.absolute_url()}/@relations"
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
            else:
                sources = [source]

        if target:
            if target[0:1] == "/":
                target = plone_api_content_get(path=target)
            else:
                target = plone_api_content_get(UID=target)
            if not target:
                return self.reply_no_content(status=404)
            else:
                targets = [target]

        if query_source:
            query_objects = {}
            if query_source[0] == "/":
                query_objects["path"] = {"query": f"{portal.id}/{query_source}"}
            else:
                query_objects["SearchableText"] = query_source
            results = catalog.searchResults(**query_objects)
            sources = [el.getObject() for el in results]

        if query_target:
            query_objects = {}
            if query_target[0] == "/":
                query_objects["path"] = {"query": query_target}
            else:
                query_objects["SearchableText"] = query_target
            results = catalog.searchResults(**query_objects)
            targets = [el.getObject() for el in results]

        data = get_relations(
            sources=sources,
            targets=targets,
            relationship=relationship,
            max=max,
            request=self.request,
        )

        result = {
            "@id": f"{self.context.absolute_url()}/@relations?{self.request['QUERY_STRING']}",
            "relations": {},
        }
        if relationship and not data:
            result["relations"][relationship] = {"items": [], "items_total": 0}
        for key in data:
            result["relations"][key] = {
                "items": data[key],
                "items_total": len(data[key]),
            }
        if relationship:
            scvq = getStaticCatalogVocabularyQuery(relationship)
            result["relations"][relationship]["staticCatalogVocabularyQuery"] = scvq
            result["relations"][relationship]["readonly"] = not api_relation_create

        return result
