# -*- coding: utf-8 -*-
from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.interfaces import IPortletManager
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getUtilitiesFor
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import providedBy


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Portlets(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal = getSite()

    def __call__(self, expand=False):
        result = {
            'navigation': {
                '@id': '{}/@navigation'.format(self.context.absolute_url()),
            },
        }
        if not expand:
            return result

        portlets_schemata = {
            iface: name
            for name, iface in getUtilitiesFor(IPortletTypeInterface)
        }
        items = {}
        for manager_name, manager in getUtilitiesFor(IPortletManager):
            mapping = queryMultiAdapter((self.context, manager),
                                        IPortletAssignmentMapping)
            if mapping is None:
                continue
            mapping = mapping.__of__(self.context)
            for name, assignment in mapping.items():
                type_ = None
                schema = None
                for schema in providedBy(assignment).flattened():
                    type_ = portlets_schemata.get(schema, None)
                    if type_ is not None:
                        break
                if type_ is None:
                    continue
                assignment = assignment.__of__(mapping)
                settings = IPortletAssignmentSettings(assignment)
                if manager_name not in items:
                    items[manager_name] = []
                items[manager_name].append({
                    'type': type_,
                    'visible': settings.get('visible', True),
                    'assignment': {
                        name: getattr(assignment, name, None)
                        for name in schema.names()
                    },
                })
        result['portlets']['items'] = items
        return result


class PortletsGet(Service):

    def reply(self):
        portlets = Portlets(self.context, self.request)
        return portlets(expand=True)['portlets']
