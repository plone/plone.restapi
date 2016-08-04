# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class ComponentsGet(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ComponentsGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@components as parameters
        for component_id in name.split(','):
            self.params.append(component_id)
        return self

    @property
    def _component_ids(self):
        return self.params

    def _wrap_component_items(self, items, component_id):
        component = {
            '@id': '{}/@components/{}'.format(
                self.context.absolute_url(),
                component_id),
            'items': items
        }
        return component

    def get_navigation(self):
        tabs = getMultiAdapter((self.context, self.request),
                               name="portal_tabs_view")
        result = []
        for tab in tabs.topLevelTabs():
            result.append({
                'title': tab.get('title', tab.get('name')),
                'url': tab['url'] + ''
            })
        return result

    def get_breadcrumbs(self):
        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name="breadcrumbs_view")
        result = []
        for crumb in breadcrumbs_view.breadcrumbs():
            result.append({
                'title': crumb['Title'],
                'url': crumb['absolute_url']
            })
        return result

    def _render_component(self, component_id):
        if component_id == 'navigation':
            items = self.get_navigation()
        elif component_id == 'breadcrumbs':
            items = self.get_breadcrumbs()
        else:
            raise NotImplementedError(
                'This endpoint does not currently support the '
                'component type %r' % component_id)

        return self._wrap_component_items(items, component_id)

    def reply(self):
        components = []
        for component_id in self._component_ids:
            components.append(self._render_component(component_id))
        return components
