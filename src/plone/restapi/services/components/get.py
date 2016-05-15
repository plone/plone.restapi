# -*- coding: utf-8 -*-
from plone.rest import Service
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

MOCKEDRESPONSE = {
    'id': 'navigation',
    'data': {
        'items': [{
            'label': 'News',
            'uri': 'http://plone/news'},
            {
            'label': 'Events',
            'uri': 'http://plone/events'
        }]
    }
}


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

    def render(self):
        return MOCKEDRESPONSE
