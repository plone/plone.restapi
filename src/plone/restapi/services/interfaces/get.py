# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import providedBy


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Interfaces(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'interfaces': {
                '@id': '{}/@interfaces'.format(self.context.absolute_url()),
            },
        }
        if not expand:
            return result

        items = []
        for item in providedBy(self.context):
            items.append(item.__identifier__)

        result['interfaces']['items'] = items
        return result


class InterfacesGet(Service):

    def reply(self):
        interfaces = Interfaces(self.context, self.request)
        return interfaces(expand=True)['interfaces']
