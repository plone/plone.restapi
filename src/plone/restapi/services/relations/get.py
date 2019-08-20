# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from z3c.relationfield.interfaces import IHasRelations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog
from plone.restapi.interfaces import ISerializeToJsonSummary


@implementer(IExpandableElement)
@adapter(IHasRelations, Interface)
class Relations(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {"relations": {"@id": "{}/@relations".format(self.context.absolute_url())}}
        if not expand:
            return result

        data = {
            "incoming": {},
            "outgoing": {}
        }

        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        intid = intids.getId(aq_inner(self.context))
        for relation_type in data.keys():
            if relation_type == "incoming":
                query = dict(to_id=intid)
            else:
                query = dict(from_id=intid)
            for rel in catalog.findRelations(query):
                if relation_type == "incoming":
                    obj = intids.queryObject(rel.from_id)
                else:
                    obj = intids.queryObject(rel.to_id)

                if obj is not None and checkPermission('zope2.View', obj):
                    summary = getMultiAdapter(
                        (obj, self.request), ISerializeToJsonSummary
                    )()
                    if rel.from_attribute in data[relation_type]:
                        data[relation_type][rel.from_attribute].append(summary)
                    else:
                        data[relation_type][rel.from_attribute] = [summary]
        result["relations"].update(data)
        return result


class RelationsGet(Service):
    def reply(self):
        relations = Relations(self.context, self.request)
        return relations(expand=True)["relations"]
