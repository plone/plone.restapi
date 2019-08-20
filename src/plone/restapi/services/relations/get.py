# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone import api
from plone.restapi.interfaces import IExpandableElement, ISerializeToJsonSummary
from plone.restapi.services import Service
from z3c.relationfield.interfaces import IHasRelations
from zc.relation.interfaces import ICatalog
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.intid.interfaces import IIntIds


@implementer(IExpandableElement)
@adapter(IHasRelations, Interface)
class Relations(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {'relations': {'@id': '{}/@relations'.format(self.context.absolute_url())}}
        if not expand:
            return result

        data = {
            'incoming': {},
            'outgoing': {}
        }

        portal_catalog = api.portal.get_tool('portal_catalog')
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        intid = intids.getId(aq_inner(self.context))
        for relation_type in data.keys():
            if relation_type == 'incoming':
                query = dict(to_id=intid)
                direction = 'from'
            else:
                query = dict(from_id=intid)
                direction = 'to'
            for rel in sorted(catalog.findRelations(query)):
                if rel.isBroken():
                    # skip broken relations
                    continue
                # query by path so we don't have to wake up any objects. Also this
                # ensures security check.
                brains = portal_catalog(path={'query': getattr(rel, direction + '_path'), 'depth': 0})
                # get summary representation from brain
                if brains is not None and len(brains):
                    summary = getMultiAdapter(
                        (brains[0], self.request), ISerializeToJsonSummary
                    )()
                    if rel.from_attribute in data[relation_type]:
                        data[relation_type][rel.from_attribute].append(summary)
                    else:
                        data[relation_type][rel.from_attribute] = [summary]
        result['relations'].update(data)
        return result


class RelationsGet(Service):
    def reply(self):
        relations = Relations(self.context, self.request)
        return relations(expand=True)['relations']
