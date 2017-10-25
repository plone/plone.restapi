# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
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
        if not expand:
            return {'@components': {'navigation': {
                '@id': '{}/@components/navigation'.format(
                    self.context.absolute_url()),
            }}}

        tabs = getMultiAdapter((self.context, self.request),
                               name="portal_tabs_view")
        result = []
        for tab in tabs.topLevelTabs():
            result.append({
                'title': tab.get('title', tab.get('name')),
                'url': tab['url'] + ''
            })
        return {'@components': {'navigation': result}}
