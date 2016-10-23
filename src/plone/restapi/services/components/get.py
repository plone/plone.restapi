# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from plone.restapi.services.components.breadcrumbs import Breadcrumbs
from plone.restapi.services.components.navigation import Navigation
from zope.deprecation import deprecate
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

    def _render_component(self, component_id):
        if component_id == 'navigation':
            items = Navigation(self.context, self.request)(expand=True)[
                '@components']['navigation']
        elif component_id == 'breadcrumbs':
            items = Breadcrumbs(self.context, self.request)(expand=True)[
                '@components']['breadcrumbs']
        else:
            raise NotImplementedError(
                'This endpoint does not currently support the '
                'component type %r' % component_id)

        return self._wrap_component_items(items, component_id)

    @deprecate(
        'The "@components" endpoint is deprecated. Please call the '
        '"@breadcrumbs" and the "@navigation" endpoints on the site root.'
    )
    def reply(self):
        components = []
        for component_id in self._component_ids:
            components.append(self._render_component(component_id))
        return components
