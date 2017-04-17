# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from zope.component import getMultiAdapter


class NavigationGet(Service):

    def reply(self):
        tabs = getMultiAdapter((self.context, self.request),
                               name="portal_tabs_view")
        result = []
        for tab in tabs.topLevelTabs():
            result.append({
                'title': tab.get('title', tab.get('name')),
                'url': tab['url'] + ''
            })
        return result
