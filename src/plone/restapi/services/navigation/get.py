# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Navigation(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'navigation': {
                '@id': '{}/@navigation'.format(self.context.absolute_url()),
            },
        }
        if not expand:
            return result

        tabs = getMultiAdapter((self.context, self.request),
                               name="portal_tabs_view")
        items = []
        for tab in tabs.topLevelTabs():
            items.append({
                'title': tab.get('title', tab.get('name')),
                '@id': tab['url'] + ''
            })
        result['navigation']['items'] = items
        return result


class NavigationGet(Service):

    def reply(self):
        navigation = Navigation(self.context, self.request)
        return navigation(expand=True)['navigation']
