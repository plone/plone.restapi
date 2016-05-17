# -*- coding: utf-8 -*-
from plone.rest import Service
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class ComponentsGet(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ComponentsGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /components_ as parameters
        for component_id in name.split(','):
            self.params.append(component_id)
        return self

    @property
    def _component_ids(self):
        return self.params

    def _frame_component_items(self, items, component_id):
        component = {
            'id': component_id,
            'data': {
                'items': items
            }
        }
        return component

    def _render_component(self, component_id):
        if component_id == 'navigation':
            items = [
                {'title': 'News',
                 'url': 'http://plone/news'},
                {'title': 'Events',
                 'url': 'http://plone/events'}
            ]
        elif component_id == 'breadcrumbs':
            items = [
                {'title': 'Junk',
                 'url': 'http://plone/junk'},
                {'title': 'More Junk',
                 'url': 'http://plone/junk/more-junk'}
            ]
        else:
            raise NotImplementedError(
                'This endpoint does not currently support the '
                'component type %r' % component_id)

        return self._frame_component_items(items, component_id)

    def render(self):
        components = []
        for component_id in self._component_ids:
            components.append(self._render_component(component_id))
        return components
